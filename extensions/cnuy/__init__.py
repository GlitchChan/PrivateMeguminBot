from necoarc import Necoarc

from .cnuy import Cnuy


def setup(client: Necoarc) -> None:
    Cnuy(client)
