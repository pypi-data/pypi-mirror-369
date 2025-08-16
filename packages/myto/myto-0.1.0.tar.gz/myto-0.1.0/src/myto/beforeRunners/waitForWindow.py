from dataclasses import dataclass
import re
from myto.base.beforeRunner import MytoBeforeRunner
import pygetwindow as gw

@dataclass(frozen=True)
class WaitForWindow(MytoBeforeRunner):
    windowMatch: str = None
    windowPattern: str = None
    isClosed: bool = False

    def __post_init__(self):
        if self.windowMatch and self.windowPattern:
            raise ValueError("Only one of 'windowMatch' or 'windowPattern' should be set, not both.")
        if not self.windowMatch and not self.windowPattern:
            raise ValueError("Either 'windowMatch' or 'windowPattern' must be set.")

    def _getTargetWindow(self):
        try:
            windows = gw.getAllWindows()
            for window in windows:
                if self.windowMatch and self.windowMatch in window.title:
                    return window
                if self.windowPattern and re.search(self.windowPattern, window.title):
                    return window
            return None
        except Exception:
            # Handle potential errors from pygetwindow
            return None

    def conditionMet(self):
        res = self._getTargetWindow()
        if self.isClosed:
            # Wait for window to close - condition met when window not found
            return res is None
        else:
            # Wait for window to open - condition met when window found
            return res is not None
