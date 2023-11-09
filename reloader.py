import sys

import pathlib, argparse
import subprocess
import logging
import shlex
import time
import json
import os

from modules.log import FancyLog
from modules.watcher import Watcher, WatcherLiveReloading
from modules.exceptions import ExceptionHandler
LOG_DIR = pathlib.Path(os.path.expanduser('~'), '.cache', 'reloader', 'logs') if (n:=os.getenv('LOG_DIR')) is None else n
logging.basicConfig(filename=os.path.join(LOG_DIR, "reloader.log"), filemode='w', level=logging.DEBUG)
console = logging.StreamHandler()
filehandler = logging.FileHandler(os.path.join(LOG_DIR, "reloader.log"), mode='w')
console.setLevel(logging.DEBUG)

formatter = FancyLog('[ %(name)s %(filename)s:%(lineno)d ][%(levelname)s] %(message)s')
file_fmt = logging.Formatter('[ %(name)s %(filename)s:%(lineno)d ][%(levelname)s] %(message)s')

console.setFormatter(formatter)
filehandler.setFormatter(file_fmt)
rl=logging.getLogger('')
rl.addHandler(console)
rl.addHandler(filehandler)
from modules.constants import LOG_DIR, RELOADER_CONFIG_PATH


logger = logging.getLogger("Reloader")

try:
    exc_obj = ExceptionHandler()
    sys.excepthook = exc_obj.global_handler
except Exception as e:
    logger.exception("Couldn't initialize ExceptionHandler()")
    logger.info("The custom exception handler will be disabled.")

parser = argparse.ArgumentParser(prog="Watcher")
parser.add_argument("--config-live-reload", action="store_true", dest="conf_live_reload", help="Adds an Inotify watcher to the config file (Not recommended)")
parser.add_argument("--traceback", action="store_true", help="Show the traceback when there's an exception")
parser.add_argument("--log-dir", dest="log_dir", help="Sets the log dir (You can set the config dir in a shell variable (LOG_DIR))")
parser.add_argument("--config-dir", dest="config_dir", help="Sets the config dir (You can set the config dir in a shell variable (RELOADER_CONFIG_PATH))")

args = parser.parse_args()

RELOADER_CONFIG_PATH=RELOADER_CONFIG_PATH if args.config_dir is None else args.config_dir
LOG_DIR=LOG_DIR if args.log_dir is None else args.log_dir

watcher = Watcher() if args.conf_live_reload is False else WatcherLiveReloading()

return_code = watcher.watch()
logger.info("modules.watcher.Watcher has been exited with return of %s", return_code)