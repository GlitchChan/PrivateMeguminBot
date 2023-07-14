from typing import Any

from interactions import Client
from loguru import _Logger, logger  # type:ignore[attr-defined]
from prisma import Prisma


class Necoarc(Client):
    """Custom Class for interactions.py."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa[ANN401]
        """Custom init."""
        super().__init__(*args, **kwargs)

        self.logger: _Logger = logger
        self.db: Prisma = Prisma(auto_register=True)
