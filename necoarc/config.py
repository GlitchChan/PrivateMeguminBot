import enlighten
import rtoml
from pydantic import BaseModel, ConfigDict, SecretStr, ValidationError

from necoarc.const import ROOT
from necoarc.log import get_logger

DEFAULT_CONFIG = """
token = ""
dev_token = ""
dev_guild = 0

[twitkit]
email = ""
username = ""
password = ""
"""


class TwitkitConfig(BaseModel):
    """Twitkit config."""
    model_config = ConfigDict(extra="ignore")

    to_track: str
    email: str
    username: SecretStr
    password: SecretStr


class Config(BaseModel):
    """Neco arc bot config."""
    model_config = ConfigDict(extra="ignore")

    token: SecretStr
    dev_token: SecretStr
    dev_guild: int
    twitkit: TwitkitConfig


_l = get_logger()
_config_path = ROOT.parent.joinpath("config.toml")
if not _config_path.exists():
    _l.warning("No config.toml found. Creating a new one.")
    _config_path.write_text(DEFAULT_CONFIG)

try:
    CONFIG = Config.model_validate(rtoml.load(_config_path))
except ValidationError:
    _l.error("Config validation failed, might be out of date!")
    _l.info("Attempting to migrate config...")

    _new = rtoml.loads(DEFAULT_CONFIG)
    _old = rtoml.load(_config_path)
    _manager = enlighten.get_manager()
    _pbar = _manager.counter(desc="Migrating config", total=len(_new) - len(_old))

    _migrate = {**_new, **{k: v for k, v in _pbar(_old.items()) if v}}
    _config_path.write_text(rtoml.dumps(_migrate, pretty=True))

    CONFIG = Config.model_validate(_migrate)
    _l.info("Migrated config successfully!")
