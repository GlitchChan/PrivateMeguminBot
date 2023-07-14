from necoarc import Necoarc

from .sexboard import Sexboard


def setup(client: Necoarc) -> None:
    Sexboard(client)
