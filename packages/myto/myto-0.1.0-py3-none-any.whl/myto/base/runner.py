

from dataclasses import field, dataclass
import logging
import os
import sys

import click
from myto.base.adapter import MytoAdapter
from myto.base.ctx import MytoCtx
from myto.base.order import DefaultOrder, MytoOrder
from myto.base.task import MytoTask


@dataclass
class MyToRunner:
    tasks : list[MytoTask] = field(default_factory=list)
    order : MytoOrder = None
    orderType : type[MytoOrder] = DefaultOrder
    ctxAdapters : list[MytoAdapter] = field(default_factory=list)
    debug : bool = False

    def __post_init__(self):
        if self.debug:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

        if self.order is None:
            self.order = self.orderType()

        if not isinstance(self.order, MytoOrder):
            raise TypeError(f"Order must be an instance of MytoOrder, got {type(self.order)}")

        if not isinstance(self.ctxAdapters, list):
            raise TypeError(f"ctxAdapters must be a list, got {type(self.ctxAdapters)}")
        
        for adapter in self.ctxAdapters:
            if not isinstance(adapter, MytoAdapter):
                raise TypeError(f"All ctxAdapters must be instances of MytoAdapter, got {type(adapter)}")

    def validate(self):
        if not self.tasks:
            raise ValueError("No tasks to run")
        
        tasknames = set()
        taskids = set()

        for task in self.tasks:
            if task.name in tasknames:
                raise ValueError(f"Duplicate task name found: {task.name}")
            if task.id in taskids:
                raise ValueError(f"Duplicate task id found: {task.id}")

            tasknames.add(task.name)
            taskids.add(task.id)

    def run(self, ctx : MytoCtx = None):
        if ctx is None:
            ctx = MytoCtx(runner=self)

        for adapter in self.ctxAdapters:
            adapter.onInit(ctx)

        for task in self.order.yieldRun(ctx):
            task : MytoTask
            logging.info(f"Running task: {task.name} (ID: {task.id})")
            ctx.push(task.id)
            

            task.exec(ctx)

            ctx.pop()

    def serialize(self):
        # wip
        return {
            "tasks": [task.serialize() for task in self.tasks],
            "order": self.order.serialize(),
            "ctxAdapters": [adapter.serialize() for adapter in self.ctxAdapters],
            "debug": self.debug
        }

    def merge(self, other : 'MyToRunner'):
        if not isinstance(other, MyToRunner):
            raise TypeError(f"Expected MyToRunner instance, got {type(other)}")

        self.tasks.extend(other.tasks)
        self.validate()
        self.ctxAdapters.extend(other.ctxAdapters)
        self.debug = self.debug or other.debug

    def mergeFromPath(self, path : str, targetVar : str = "runner"):
        assert os.path.exists(path), f"Path does not exist: {path}"
        # Load the MyToRunner instance from the specified path
        if os.path.isdir(path):
            targets = [os.path.join(path, x) for x in os.listdir(path) if x.endswith(".py")]
        else:
            targets = [path]
        for target in targets:
            gmap = {}
            with open(target, 'r') as f:
                code = f.read()
            
            exec(code, gmap)
            if targetVar not in gmap:
                click.echo(f"Runner not found in {target}: {targetVar}")
                continue
            
            baseRunner = gmap[targetVar]
            self.merge(baseRunner)