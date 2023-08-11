from interactions import Client

from .cnuy import Cnuy


def setup(client: Client) -> None:
    Cnuy(client)
