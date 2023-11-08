import logging
import pathlib
import subprocess
from modules.constants import LOG_DIR

class AgsProcess:
    def __init__(self):
        self.logger = logging.getLogger("AgsProcess")
        self.logger.info("Starting ags for the first time...")
        self.ags_log_file = pathlib.Path(LOG_DIR, "ags.log").open("w")
        self.proc = self.run_ags()

    def run_ags(self, proc=None):
        self.logger.debug("Proc value: %s", proc)
        if proc is not None:
            pid = proc.pid
            self.logger.info("Killing ags...")
            proc.kill()
            self.logger.info("Killed ags with pid of: %d", pid)
        self.logger.info("Starting ags...")

        # return subprocess.Popen(["ags"], stdout=self.ags_log_file, stderr=self.ags_log_file)
        return subprocess.Popen(["ags"])
