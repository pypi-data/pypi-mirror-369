
from dataclasses import dataclass
import datetime

invalid_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)

@dataclass
class WhenTime:
    hours : int
    minutes : int = 0
    seconds : int = 0
    am : bool = False
    pm : bool = False

    def __post_init__(self):
        assert isinstance(self.hours, int) and 0 <= self.hours < 24
        assert isinstance(self.minutes, int) and 0 <= self.minutes < 60
        assert isinstance(self.seconds, int) and 0 <= self.seconds < 60
        assert isinstance(self.am, bool)
        assert isinstance(self.pm, bool)

        if self.am:
            self.pm = False
        elif self.pm:
            self.am = False
        else:
            self.pm = True

        if self.hours > 12:
            self.pm = True
            self.hours -= 12

    def _todatetime(self):
        now = datetime.datetime.now()
        return datetime.datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=self.hours + (12 if self.pm else 0),
            minute=self.minutes,
            second=self.seconds
        )

    def when(self, ctx) -> datetime.datetime | None:
        target_time = self._todatetime()
        now = datetime.datetime.now()

        if target_time < now:
            # If the target time is in the past, return None
            return invalid_datetime

        # Return the target time if it's in the future
        return target_time    
