from necoarc import Necoarc

from .funny import Funny


def setup(client: Necoarc) -> None:
    Funny(client)
