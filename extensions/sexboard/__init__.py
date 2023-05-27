from .sexboard import Sexboard


def setup(client) -> None:  # type: ignore[no-untyped-def]
    Sexboard(client)
