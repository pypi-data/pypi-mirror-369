import logging
import os
from logging import NullHandler
from rich.logging import RichHandler

# Get the library's top-level logger. When this file is imported,
# __name__ will be 'lgopy'.
logger = logging.getLogger(__name__)

# Add a NullHandler to prevent "No handler found" warnings. This is the
# standard practice for libraries. It does nothing by default, leaving the
# application that uses this library in control of logging configuration.
logger.addHandler(NullHandler())

__version__ = "1.5.6"


def setup_logging(
    level: str | int = "INFO",
    enable_rich_tracebacks: bool = False,
) -> None:
    """
    Set up logging for the lgopy library using rich for beautiful output.

    This is an optional convenience function. Call this in your application's
    entry point to see formatted log messages from the lgopy library.

    Args:
        level: The minimum logging level to output (e.g., "DEBUG", "INFO").
               Defaults to "INFO". Can be overridden by the LGO_LOG_LEVEL
               environment variable.
        enable_rich_tracebacks: If True, unhandled exceptions will be
                                formatted by rich for better readability.
                                Defaults to False for cleaner output.
    """

    # Allow overriding log level with an environment variable for convenience.
    log_level = os.environ.get("LGO_LOG_LEVEL", str(level)).upper()

    # Get the logger for the 'lgopy' package.
    lib_logger = logging.getLogger("lgopy")
    lib_logger.setLevel(log_level)

    # Create a rich handler for console output.
    # You can customize show_time, show_level, show_path, etc. as needed.
    handler = RichHandler(
        rich_tracebacks=enable_rich_tracebacks,
        show_path=False,  # Set to True to see file and line number
        markup=True,      # Allow rich markup in log messages
    )

    # Clear existing handlers to avoid duplicate messages if this is called multiple times.
    if lib_logger.hasHandlers():
        lib_logger.handlers.clear()

    lib_logger.addHandler(handler)

    # By default, log messages are propagated to the root logger.
    # You can set this to False if you want to handle lgopy logs exclusively.
    # lib_logger.propagate = False

    logger.info(f"Rich logging configured for 'lgopy' at level [bold green]{log_level}[/bold green].", extra={"markup": True})

setup_logging()