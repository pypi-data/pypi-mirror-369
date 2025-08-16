
from dataclasses import dataclass
import random
import re

from myto.base.ctx import MytoCtx
from myto.base.when import MytoWhen

_forward_counter = 0
_global_id = set()

def id_parse(name: str) -> str:
    # Parse the ID from the name
    id = name.replace(" ", "_").lower()
    id = re.sub(r'[^a-zA-Z0-9_]', '', id)
    return id

@dataclass
class MytoTask:
    name : str = None
    description : str = None
    id : str = None
    idParseMethod : callable = id_parse
    taskDefaultNameFormat : str = "Task-{id}"
    when : MytoWhen = None

    def __post_init__(self):
        global _forward_counter
        if self.name is None:
            _forward_counter += random.randint(1, 10)
            self.name = self.taskDefaultNameFormat.format(id=_forward_counter)

        if self.id is None:
            self.id = self.idParseMethod(self.name)

        if self.id in _global_id:
            raise ValueError(f"Duplicate task id found: {self.id}")
        _global_id.add(self.id)

    def exec(self, ctx : MytoCtx):
        raise NotImplementedError("Subclasses must implement this method")
    
    def __hash__(self):
        return hash(self.id)
    
    def serialize(self):
        return {
            "type" : self.__class__.__name__,
            "name": self.name,
            "description": self.description,
            "id": self.id,
            "when": self.when.serialize() if self.when else None
        }