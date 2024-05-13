import logging
import sys
import typing

from loguru import logger

from necoarc.const import DEBUG, ROOT

__all__ = ("get_logger",)

if typing.TYPE_CHECKING:
    from loguru import Logger


_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
           "<r>|</r> <le><b>{extra}</b></le> "
           "<r>|</r> <level>{level.icon} {level: <6}</level> "
           "<r>|</r> <cyan>{name}</cyan><r>:</r><cyan>{function}</cyan><r>:</r><cyan>{line}</cyan> "
           "<r>|</r> <level>{message}</level>"
           )
_log_path = ROOT.parent.joinpath("logs/necoarc.log")


def get_logger() -> "Logger":
    """Function to get a customized loguru logger."""
    logger.remove()  # Remove all handlers added so far, including the default one.
    logger.add(  # Base Logger
        sys.stdout,
        level=logging.INFO if not DEBUG else logging.DEBUG,
        enqueue=True,
        format=_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
        catch=True,
    )

    logger.add(  # File logger
        _log_path,
        level=logging.INFO if not DEBUG else logging.DEBUG,
        rotation="00:00",
        retention="7 days",
        enqueue=True,
        format=_format,
        colorize=False,
        backtrace=True,
        diagnose=True,
        catch=True,
        compression="tar.gz"
    )

    return logger
