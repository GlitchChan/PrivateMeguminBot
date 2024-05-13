import sys

from necoarc import NecoArc
from necoarc.config import CONFIG
from necoarc.const import DEBUG

if __name__ == "__main__":
    if not CONFIG.token or CONFIG.dev_token:
        from necoarc.log import get_logger

        get_logger().error("You do not have a discord token configured!")
        sys.exit(1)
    token = CONFIG.token.get_secret_value() if not DEBUG else CONFIG.dev_token.get_secret_value()
    NecoArc().start(token)
