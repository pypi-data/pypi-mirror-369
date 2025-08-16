

from dataclasses import dataclass
import logging
import subprocess
from myto.base.task import MytoTask


@dataclass
class OpenAppTask(MytoTask):
    appName : str = None
    appNameMethod : callable = None
    isPath : bool = True
    shouldDetach : bool = True

    def __post_init__(self):
        super().__post_init__()
        if self.appName is None and self.appNameMethod is None:
            raise ValueError("App name or method must be specified")

    def exec(self, _):
        if self.appNameMethod:
            self.appName = self.appNameMethod()
        logging.info(f"Opening application: {self.appName}")

        if self.isPath:
            if self.shouldDetach:
                subprocess.Popen(self.appName, shell=True, start_new_session=True)
                logging.info(f"Application opened (detached): {self.appName}")
            else:
                subprocess.run(self.appName, shell=True)
                logging.info(f"Application opened: {self.appName}")
        else:
            if self.shouldDetach:
                subprocess.Popen(self.appName, shell=True, start_new_session=True)
                logging.info(f"Application executed (detached): {self.appName}")
            else:
                subprocess.run(self.appName, shell=True)
                logging.info(f"Application executed: {self.appName}")

