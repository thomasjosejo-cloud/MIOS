"""Executable entrypoint: `python -m mios`."""

import uvicorn

from mios.config import get_settings


def main() -> None:
    """Run the application with the configured host and port."""
    settings = get_settings()
    uvicorn.run(
        "mios.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
