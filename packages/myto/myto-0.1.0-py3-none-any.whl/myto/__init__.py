from myto.base.runner import MyToRunner
from myto.utils.clsprop import classproperty

class _beforeRunners:
    @classproperty
    def waitForProcess(cls):
        from .beforeRunners.waitForProcess import WaitForProcess
        return WaitForProcess
    
    @classproperty
    def waitForWindow(cls):
        from .beforeRunners.waitForWindow import WaitForWindow
        return WaitForWindow

class Myto:
    runner = MyToRunner
    beforeRunners = _beforeRunners
    