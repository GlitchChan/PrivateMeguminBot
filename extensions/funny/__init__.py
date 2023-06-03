from interactions import Client

from .funny import Funny


def setup(client: Client) -> None:
    Funny(client)
