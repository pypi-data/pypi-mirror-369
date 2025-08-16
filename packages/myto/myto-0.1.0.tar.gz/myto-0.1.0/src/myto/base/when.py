
import datetime

class MytoWhen:
    def when(self, ctx) -> datetime.datetime | None:
        return None

    def serialize(self):
        return {
            "type": self.__class__.__name__,
        }