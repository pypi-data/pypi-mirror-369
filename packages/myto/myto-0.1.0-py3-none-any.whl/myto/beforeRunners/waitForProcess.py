
from dataclasses import dataclass
import re
from myto.base.beforeRunner import MytoBeforeRunner
import psutil

@dataclass(frozen=True)
class WaitForProcess(MytoBeforeRunner):
    processMatch : str = None
    processPattern : str = None
    isClosed : bool = False

    def __post_init__(self):
        if self.processMatch and self.processPattern:
            raise ValueError("Only one of 'processMatch' or 'processPattern' should be set, not both.")

    def _getTargetProcess(self):
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if self.processMatch and self.processMatch in proc.info['name']:
                return proc
            if self.processPattern and re.search(self.processPattern, proc.info['name']):
                return proc
        return None

    def conditionMet(self):
        res = self._getTargetProcess()
        if self.isClosed:
            # Wait for process to close - condition met when process not found
            return res is None
        else:
            # Wait for process to start - condition met when process found
            return res is not None