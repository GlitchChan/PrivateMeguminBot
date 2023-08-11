from interactions import Client

from .sexboard import Sexboard


def setup(client: Client) -> None:
    Sexboard(client)
