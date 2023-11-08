from modules.config import Config
import logging
import pathlib
import os

CONF_DIR = pathlib.Path(os.path.expanduser('~'), '.config', 'ags', 'src') if (n:=os.getenv('CONF_DIR')) is None else n
RELOADER_CONFIG_PATH = pathlib.Path(os.path.join(CONF_DIR, "reload", 'reloader.json'))

LOG_DIR = pathlib.Path(os.path.expanduser('~'), '.cache', 'reloader', 'logs') if (n:=os.getenv('LOG_DIR')) is None else n
LOG_DIR.mkdir(parents=True, exist_ok=True)

conf_obj = Config(RELOADER_CONFIG_PATH, create_if_not_exist=True, default_config={"files": []})
CONFIG = conf_obj.load()
FILES = conf_obj.config_to_object("files", pathlib.Path)

logger = logging.getLogger("Constants")

logger.info("CONF_DIR has been set to: %s", CONF_DIR)
logger.info("LOG_DIR has been set to: %s", LOG_DIR)
