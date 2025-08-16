
from dataclasses import dataclass
import datetime

from myto.base.when import MytoWhen


@dataclass
class WhenTimer(MytoWhen):
    seconds : int = None
    minutes : int = None
    hours : int = None

    def __post_init__(self):
        self._onInitDt = datetime.datetime.now()
        self._target = self._onInitDt + datetime.timedelta(seconds=self._total)

    @property
    def _total(self):
        total = 0
        if self.seconds is not None:
            total += self.seconds
        if self.minutes is not None:
            total += self.minutes * 60
        if self.hours is not None:
            total += self.hours * 3600
        return total
    
    def when(self, ctx):
        return self._target