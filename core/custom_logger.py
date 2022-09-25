import os
import sys
from distutils.util import strtobool

import jurigged
from loguru import logger as log

log.remove()
log.add(
    "logs/megumin.log",
    backtrace=True,
    enqueue=True,
    diagnose=True,
    rotation="12:00",
    retention="10 days",
)
log.add(sys.stdout, level="DEBUG" if strtobool(os.getenv("DEBUG")) else "INFO", enqueue=True)
log.level("JURIG", no=11, color="<fg #3a304e>")


def jlogger(event: object) -> None:
    """Logging for jurigged

    :param event: Event to parse
    :return: None
    """
    if isinstance(event, jurigged.live.WatchOperation):
        log.log("JURIG", f"Watch {event.filename}")
    elif isinstance(event, jurigged.codetools.AddOperation):
        event_str = f"{event.defn.parent.dotpath()}:{event.defn.stashed.lineno}"
        if isinstance(event.defn, jurigged.codetools.LineDefinition):
            event_str += f" | {event.defn.text}"
            log.log("JURIG", f"Run {event_str}")
        else:
            log.log("JURIG", f"Add {event_str}")
    elif isinstance(event, jurigged.codetools.UpdateOperation):
        if isinstance(event.defn, jurigged.codetools.FunctionDefinition):
            event_str = f"{event.defn.parent.dotpath()}:{event.defn.stashed.lineno}"
            log.log("JURIG", f"Update {event_str}")
    elif isinstance(event, (Exception, SyntaxError)):
        log.opt(exception=True).exception("Jurigged encountered error")
    else:
        log.log("JURIG", event)
