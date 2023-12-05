import json
import pathlib
import logging
import threading

try: 
    from inotify.adapters import Inotify
    import inotify.constants as masks
except ImportError:
    import sys
    print("Please source the virtual environment first.")
    print("$ source venv/bin/activate")
    sys.exit(1)

class Config:
    def __init__(self, path: str | pathlib.Path, create_if_not_exist: bool = True, default_config: dict = None) -> None:
        if isinstance(path, str):
            path = pathlib.Path(path)
        self.logger = logging.getLogger("Config")
        if path.exists() is False:
            self.logger.info("Config doesn't exists")
            if create_if_not_exist:
                if default_config is None:
                    self.logger.fatal("Default config not defined")
                    raise FileNotFoundError(f"Config file not found at {path}")
                self.logger.info("Creating config file")
                self.config = default_config
                path.write_text(json.dumps(default_config, indent=4))

        self.config_path = path
        self.running = False
        self.thread = None
        self.config = None

    def load(self) -> dict:
        self.logger.info("Loading config...")
        self.config = json.loads(self.config_path.read_text())
        return self.config
    
    def get_config(self) -> dict | None:
        return self.config

    def update(self, new_config: dict) -> dict:
        self.logger.info("Updating config...")
        self.config.update(new_config)
        self.config_path.write_text(json.dumps(self.config))
        return self.config

    def config_to_object(self, key: str, obj, callback=lambda x: x) -> list:
        for x in self.config[key]:
            self.logger.debug(f"Converting {x} to {obj}")
            value = callback(x)
            if type(value) is list:
                for y in value:
                    yield obj(y)
            else:
                yield obj(value)
        
    def watch_for_config_changes(self, callback, args: list = []) -> None:
        self.thread = threading.Thread(target=self._watch_conf, args=[callback, args])
        self.thread.start()
        self.logger.info("Watcher for config file %s has been set", self.config_path)
    
    def stop_config_watcher(self):
        self.running = False

    def _watch_conf(self, callback, args: list) -> None:
        if callable(callback) is False:
            raise TypeError(f"Expected a function, {type(callback)} gived")
        watcher = Inotify()
        watcher.add_watch(str(self.config_path), mask=masks.IN_MODIFY | masks.IN_IGNORED)
        for event in watcher.event_gen(yield_nones=False):
            self.logger.debug("New event from config file: %s", event)
            self.logger.debug("Reading config...")
            try:
                self.load()
            except:
                self.logger.warning("Error when loading config.")
                self.logger.exception("More info:")
                continue
            
            self.logger.debug(f"Calling callback... ({callback})")
            callback(*args)