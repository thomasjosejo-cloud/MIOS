"""Live engine orchestrator.

Owns the background polling loop that drives the whole pipeline:

    fetch (MarketDataSource) -> run_pipeline -> update in-memory store
                             -> persist snapshots -> log changes

The loop is resilient: a failed poll is logged and recorded on the store, then
the loop waits and retries rather than dying. Structured logs are emitted for
data received, classification changes, recommendation changes, and errors.
"""

import asyncio
import datetime as dt
import time
from collections.abc import Awaitable, Callable
from decimal import Decimal

from mios.config import Settings
from mios.core.logging import get_logger
from mios.db.session import Database
from mios.integrations.fyers.client import FyersAuthError
from mios.integrations.fyers.market_data import MarketDataSource
from mios.schemas.market import (
    Classification,
    ClassificationResult,
    OptionType,
    TradeQualification,
)
from mios.services.options_intel import snapshot_repository
from mios.services.options_intel.option_engine import OptionEngine
from mios.services.options_intel.pipeline import PipelineResult, run_pipeline
from mios.services.options_intel.store import EngineStore

logger = get_logger(__name__)

ClassificationMap = dict[tuple[Decimal, OptionType], Classification]


class OptionsIntelEngine:
    """Coordinates polling, analysis, persistence, and change logging."""

    def __init__(
        self,
        source: MarketDataSource,
        store: EngineStore,
        database: Database,
        settings: Settings,
        *,
        on_session_expired: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        """Wire the orchestrator to its source, store, database, and settings.

        `on_session_expired` is invoked once if a poll fails authentication
        (the Fyers token was rejected mid-session), letting the caller stop the
        engine and clear the session without coupling this class to auth.
        """
        self._source = source
        self._store = store
        self._database = database
        self._settings = settings
        self._on_session_expired = on_session_expired
        self._option_engine = OptionEngine()
        self._task: asyncio.Task[None] | None = None
        self._stopping = asyncio.Event()
        self._previous_classifications: ClassificationMap = {}
        self._previous_qualification: tuple[str, str, int] | None = None

    def start(self) -> None:
        """Launch the polling loop as a background task."""
        if self._task is not None:
            return
        self._stopping.clear()
        self._store.engine_running = True
        self._task = asyncio.create_task(self._run_loop(), name="options-intel-engine")
        logger.info(
            "Options intelligence engine started",
            extra={"poll_interval_s": self._settings.ENGINE_POLL_INTERVAL_SECONDS},
        )

    async def stop(self) -> None:
        """Signal the loop to stop and wait for the current poll to finish."""
        if self._task is None:
            return
        self._stopping.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
        self._store.engine_running = False
        logger.info("Options intelligence engine stopped")

    async def _run_loop(self) -> None:
        """Poll on the configured interval until stopped."""
        interval = self._settings.ENGINE_POLL_INTERVAL_SECONDS
        while not self._stopping.is_set():
            try:
                await self.poll_once()
            except asyncio.CancelledError:
                raise
            except FyersAuthError as error:
                # The Fyers token was rejected mid-session (expired/revoked):
                # stop polling and hand off to the caller to clear the session.
                self._store.last_error = f"{type(error).__name__}: {error}"
                self._store.engine_running = False
                logger.warning("Fyers session expired during polling; stopping")
                if self._on_session_expired is not None:
                    await self._on_session_expired()
                return
            except Exception as error:
                self._store.last_error = f"{type(error).__name__}: {error}"
                logger.exception("Poll failed; engine will retry")
            try:
                await asyncio.wait_for(self._stopping.wait(), timeout=interval)
            except TimeoutError:
                continue

    async def poll_once(self) -> None:
        """Run a single poll: fetch, analyze, store, persist, and log changes."""
        source = self._source
        market_open = await source.get_market_open()
        spot = await source.get_spot()
        option_quotes = await source.get_option_chain()

        # History (5-minute candles) is the optional validation step. Its
        # failure must not stop the engine: quotes and the option chain above
        # are the required inputs. When history is unavailable we proceed with
        # no candles — Structure and Momentum degrade to their neutral
        # "insufficient history" result, so context and recommendations are
        # still produced. Quotes/chain errors above are still fatal to the poll.
        try:
            candles = await source.get_candles()
            validation_available = True
        except Exception as error:
            candles = []
            validation_available = False
            logger.warning(
                "History unavailable; skipping validation, continuing with "
                "option-chain intelligence",
                extra={"error": f"{type(error).__name__}: {error}"},
            )

        logger.info(
            "Market data received",
            extra={
                "spot": str(spot.ltp),
                "strikes": len(option_quotes),
                "candles": len(candles),
                "market_open": market_open,
                "validation": "available" if validation_available else "unavailable",
            },
        )

        started = time.perf_counter()
        result = run_pipeline(
            option_engine=self._option_engine,
            option_quotes=option_quotes,
            candles=candles,
            spot=spot.ltp,
            settings=self._settings,
            previous_cepe=self._store.cepe,
        )
        runtime_ms = (time.perf_counter() - started) * 1000

        self._apply_to_store(
            result,
            spot_price=spot.ltp,
            market_open=market_open,
            validation_available=validation_available,
        )
        self._log_classification_changes(result.classifications)
        self._log_qualification_change(result.qualification)
        await self._persist(result)

        self._store.last_pipeline_runtime_ms = runtime_ms
        self._store.last_poll_at = dt.datetime.now(dt.UTC)
        self._store.last_error = None

    def _apply_to_store(
        self,
        result: PipelineResult,
        *,
        spot_price: Decimal,
        market_open: bool,
        validation_available: bool,
    ) -> None:
        """Copy a pipeline result and metadata into the shared store."""
        store = self._store
        store.previous_spot_price = store.spot_price
        store.previous_controlling_side = (
            store.context.controlling_side if store.context else None
        )
        store.validation_available = validation_available
        store.strike_states = result.strike_states
        store.classifications = result.classifications
        store.unusual = result.unusual
        store.radar = result.radar
        store.cepe = result.cepe
        store.bias = result.bias
        store.structure = result.structure
        store.momentum = result.momentum
        store.context = result.context
        store.qualification = result.qualification
        store.spot_price = spot_price
        store.market_open = market_open

    def _log_classification_changes(
        self, classifications: list[ClassificationResult]
    ) -> None:
        """Log only strikes whose classification changed since the previous poll."""
        current: ClassificationMap = {}
        for result in classifications:
            key = (result.strike, result.option_type)
            current[key] = result.classification
            previous = self._previous_classifications.get(key)
            if previous != result.classification:
                logger.info(
                    "Classification changed",
                    extra={
                        "strike": str(result.strike),
                        "option_type": result.option_type.value,
                        "from": previous.value if previous else None,
                        "to": result.classification.value,
                    },
                )
        self._previous_classifications = current

    def _log_qualification_change(self, qualification: TradeQualification) -> None:
        """Log when the qualification decision changes."""
        signature = (
            qualification.decision.value,
            str(qualification.strike),
            qualification.confidence,
        )
        if self._previous_qualification != signature:
            logger.info(
                "Qualification changed",
                extra={
                    "decision": qualification.decision.value,
                    "strike": str(qualification.strike),
                    "confidence": qualification.confidence,
                    "failed_gates": [g.value for g in qualification.failed_gates],
                },
            )
        self._previous_qualification = signature

    async def _persist(self, result: PipelineResult) -> None:
        """Persist the poll's snapshots, tolerating a disconnected database."""
        if not self._database.is_connected:
            return
        async with self._database.transaction() as session:
            count = await snapshot_repository.persist_snapshots(
                session,
                result.strike_states,
                result.classifications,
                symbol=self._settings.NIFTY_SPOT_SYMBOL,
            )
        logger.debug("Persisted snapshots", extra={"rows": count})
