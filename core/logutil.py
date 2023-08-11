import logging
from pathlib import Path

from rich.logging import RichHandler
from rich.traceback import install

install()


def init_logger(name: str, debug: bool = False) -> logging.Logger:  # noqa: FBT002
    """Custom function to get a rich logger.

    Args:
        name (str): Name of logger
        debug (bool): Debug logging
    Returns:
        logger (logging.Logger)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = RichHandler(
        markup=True, rich_tracebacks=True, tracebacks_show_locals=debug, log_time_format="%x %H:%M:%S.%f"
    )
    logger.addHandler(handler)
    file_handler = logging.FileHandler(
        filename=Path(__file__).parent.parent / "logs/necoarc.log", encoding="UTF-8", mode="w"
    )
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)8s] %(message)s"))
    logger.addHandler(file_handler)

    return logger
