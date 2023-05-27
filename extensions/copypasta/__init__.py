from .copypasta import Copypasta


def setup(client) -> None:  # type: ignore[no-untyped-def]
    Copypasta(client)
