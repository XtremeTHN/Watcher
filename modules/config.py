import json
import pathlib
import logging

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
    
    def load(self) -> dict:
        self.logger.info("Loading config...")
        self.config = json.loads(self.config_path.read_text())
        return self.config

    def update(self, new_config: dict) -> dict:
        self.logger.info("Updating config...")
        self.config.update(new_config)
        self.config_path.write_text(json.dumps(self.config))
        return self.config

    def config_to_object(self, key: str, obj) -> list:
        for x in self.config[key]:
            self.logger.debug(f"Converting {x} to {obj}")
            yield obj(x)
        
    def watch_for_changes(self) -> None:
        self.logger.info("Watcher for config file %s has been set", self.config_path)