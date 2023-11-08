import sys


import subprocess
import logging
import shlex
import time
import json
import os

from modules.log import FancyLog
from modules.watcher import Watcher
from modules.exceptions import ExceptionHandler
import pathlib

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
from modules.constants import LOG_DIR, CONF_DIR


logger = logging.getLogger("Reloader")

try:
    exc_obj = ExceptionHandler()
    sys.excepthook = exc_obj.global_handler
except Exception as e:
    logger.exception("Couldn't initialize ExceptionHandler()")
    logger.info("The custom exception handler will be disabled.")

watcher = Watcher()
watcher.watch()