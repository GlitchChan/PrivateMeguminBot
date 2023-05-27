from .funny import Funny


def setup(client) -> None:  # type: ignore[no-untyped-def]
    Funny(client)
