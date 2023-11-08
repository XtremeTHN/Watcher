import threading
import pathlib
import logging
import sys
import os

from modules.constants import CONF_DIR, FILES
from modules.ags import AgsProcess

try: 
    import inotify.adapters as watcher
    import inotify.constants as masks
except ImportError:
    print("Please source the virtual environment first.")
    print("$ source venv/bin/activate")
    sys.exit(1)

class Watcher:
    def __init__(self):
        self.logger = logging.getLogger("Watcher")

        self.logger.info("Starting inotify.adapters.InotifyTree...")
        self.logger.info("Initializing inotify.adapters.InotifyTree...")
        
        self.intfy = watcher.Inotify()

        root_dir = os.path.dirname(CONF_DIR)
        default_paths = [os.path.join(root_dir, 'config.js'), os.path.join(CONF_DIR, 'bar.js'), os.path.join(CONF_DIR, 'widgets.js'), os.path.join(CONF_DIR, 'styles', "style.css")]

        self.ags_class = AgsProcess()
        self.add_watches(default_paths, defaults=True)
        self.add_watches(FILES)

    def add_watches(self, paths: list, defaults=False):
        if defaults is True:
            if os.path.exists(paths[0]) is False:
                self.logger.error("Main file not found!")
                self.logger.warning("Ignoring %s...", paths.pop(0))
        for x in paths:
            x = pathlib.Path(x)
            if x.exists() is False:
                self.logger.warning("File not found: %s", str(x))
                self.logger.warning("Ignoring it...")
                continue
            self.intfy.add_watch(str(x), mask=masks.IN_MODIFY)
    def watch(self):
        self.logger.info("Entering to the main loop...")
        try:
            for event in self.intfy.event_gen(yield_nones=False):
                self.logger.debug("Event: %s", event)
                self.restart()
        except KeyboardInterrupt:
            self.logger.info("Exiting...")

    def restart(self):
        self.ags_class.proc = self.ags_class.run_ags(self.ags_class.proc)