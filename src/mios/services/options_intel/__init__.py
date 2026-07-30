"""Options Intelligence pipeline.

Fyers -> Normalizer (in `mios.integrations.fyers`) -> Option Engine ->
Classification / Unusual Activity / Radar / CE-PE -> Structure -> Momentum ->
Context -> Recommendation / No-Trade.

This pipeline is intentionally direct rather than event-bus-mediated: engines
call one another's pure functions in sequence, and the Option Engine calls the
configured `MarketDataSource` (Fyers or simulated) directly. This diverges
from the Event-Bus-mediated, provider-isolated architecture described in
`docs/04-data-layer.md` and the Analysis Engine specs in `docs/09` through
`docs/13` (which forbid direct external connectivity and direct engine-to-
engine calls); the divergence was an explicit, discussed decision for this
sprint, not an oversight.
"""
