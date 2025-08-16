

from collections.abc import Generator
import datetime
import logging
from time import sleep
from myto.base.ctx import MytoCtx
from myto.base.task import MytoTask

class MytoOrder:
    def yieldRun(self, ctx : MytoCtx) -> Generator[MytoTask, None, None]:
        # get no when tasks 
        tasks : list[MytoTask] = ctx.runner.tasks
        now = datetime.datetime.now()
        
        # Tasks with no when condition OR when condition that should run now/in the past
        nowhentasks = []
        yeswhentasks = []
        
        for task in tasks:
            if not task.when:
                # No when condition - run immediately
                nowhentasks.append(task)
            else:
                when_time = task.when.when(ctx)
                if when_time is None or when_time <= now:
                    # When condition is met (None means run now, or time has passed)
                    nowhentasks.append(task)
                else:
                    # When condition is in the future
                    yeswhentasks.append(task)

        for task in nowhentasks:
            logging.info(f"Dispatching task: {task.name}")
            yield task
        
        timedTasks = {}
        for task in yeswhentasks:
            nextRuntime = task.when.when(ctx)
            # check if its no longer within current day, or time is already passed
            if nextRuntime is None or nextRuntime < now or nextRuntime.date() != now.date():
                continue

            timedTasks[nextRuntime] = task


        # sort by closest
        timedTasks = sorted(timedTasks.items(), key=lambda x: x[0])
        try:
            while True:
                if not timedTasks:
                    break
                
                nextRuntime, task = timedTasks[0]
                now = datetime.datetime.now()

                if nextRuntime <= now:
                    logging.info(f"Dispatching timed task: {task.name}, {nextRuntime}")
                    yield task
                    timedTasks.pop(0)
                
                sleep(1)
                
        except KeyboardInterrupt:
            return    


class DefaultOrder(MytoOrder):
    pass
