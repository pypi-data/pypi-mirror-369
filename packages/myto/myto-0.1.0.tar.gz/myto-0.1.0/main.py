from myto.base.runner import MyToRunner
from myto.tasks.openAppTask import OpenAppTask
from myto.when.timer import WhenTimer

runner = MyToRunner(
    tasks=[
        OpenAppTask(
            appName="notepad.exe",
            when=WhenTimer(
                seconds=10
            )
        ),
        OpenAppTask(
            appName="start pwsh.exe",
        )
    ],
    debug=True
)