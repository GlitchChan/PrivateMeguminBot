from peewee import BigIntegerField, Model, SqliteDatabase
from rocksdict import Rdict

from necoarc.const import ROOT

__all__ = ("User", "Server", "rd_db", "pw_db")


PEEWEE_PATH = ROOT.parent.joinpath("database.db")
RDICT_PATH = ROOT.joinpath("data")
pw_db = SqliteDatabase(PEEWEE_PATH)
rd_db = Rdict(RDICT_PATH.as_posix())


class BaseModel(Model):  # type: ignore[misc]
    """Base class for all models."""
    class Meta:
        """Meta class."""
        database = pw_db


class User(BaseModel):
    """Discord User model."""
    id = BigIntegerField(primary_key=True, unique=True)
    sex_count = BigIntegerField(default=1)


class Server(BaseModel):
    """Discord Server model."""
    id = BigIntegerField(primary_key=True, unique=True)
    confess_channel = BigIntegerField(null=True)
    cnuy_channel = BigIntegerField(null=True)
