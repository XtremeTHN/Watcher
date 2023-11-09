import threading
import pathlib
import logging
import sys
import os

from modules.constants import conf_obj, FILES
from modules.ags import AgsProcess

try: 
    import inotify.adapters as watcher
    import inotify.constants as masks
except ImportError:
    print("Please source the virtual environment first.")
    print("$ source venv/bin/activate")
    sys.exit(1)

class WatcherLiveReloading(watcher.Inotify):
    def __init__(self):
        self.logger = logging.getLogger("Watcher")
        self.logger.info("Initializing inotify.adapters.InotifyTree...")
        super().__init__()

        self.logger.info("Starting config reloader...")
        conf_obj.watch_for_config_changes(self.update_watchers)

        self.ags_class = AgsProcess()
        self.current_paths = FILES

    def add_watchers(self, paths: list=None):
        paths = self.current_paths if paths is None else paths
        for x in paths:
            if x.exists() is False:
                self.logger.warning("File not found: %s", str(x))
                self.logger.warning("Ignoring it...")
                continue
            self.add_watch(str(x), mask=masks.IN_MODIFY)

    def watch(self):
        self.logger.info("Entering to the main loop...")
        try:
            local_current_paths = self.current_paths
            while True:
                super().__init__()
                self.add_watchers()
                for event in self.event_gen(yield_nones=False):
                    if self.current_paths != local_current_paths:
                        local_current_paths = self.current_paths
                        break
                    self.logger.debug("Event: %s", event)
                    self.restart()
        except KeyboardInterrupt:
            return None

    def restart(self):
        self.ags_class.proc = self.ags_class.run_ags(self.ags_class.proc)

    def update_watchers(self):
        self.logger.info("Adding new watchers...")
        self.current_paths = list(conf_obj.config_to_object('files', pathlib.Path))

    def remove_watchers(self):
        self.logger.info("Removing current watchers...")
        if self.current_paths is not None or []:
            self.logger.info(self.current_paths)
            for x in self.current_paths:
                self.logger.info("Removing %s...", x)
                self.remove_watch(x, superficial=True)
        else:
            self.logger.info("No current watchers")

class Watcher:
    def __init__(self):
        self.logger = logging.getLogger("Watcher")

        self.logger.info("Starting inotify.adapters.InotifyTree...")
        self.logger.info("Initializing inotify.adapters.InotifyTree...")
        
        self.intfy = watcher.Inotify()

        self.ags_class = AgsProcess()
        self.add_watches(FILES)

    def add_watches(self, paths: list):
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