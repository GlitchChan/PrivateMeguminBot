from necoarc import Necoarc

from .copypasta import Copypasta


def setup(client: Necoarc) -> None:
    Copypasta(client)
