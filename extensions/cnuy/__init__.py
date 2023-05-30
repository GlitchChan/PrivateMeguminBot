from .cnuy import Cnuy


def setup(client) -> None:  # type: ignore[no-untyped-def]
    Cnuy(client)
