from interactions import Client

from .copypasta import Copypasta


def setup(client: Client) -> None:
    Copypasta(client)
