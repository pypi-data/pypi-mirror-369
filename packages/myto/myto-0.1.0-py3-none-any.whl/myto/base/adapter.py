

class MytoAdapter:
    """
    Adapters are invoked before, after, 
    or optionally during task execution.
    """

    def onInit(self, ctx):
        pass

    def before(self, ctx, task, flag: str = None, **kwargs):
        raise NotImplementedError("This adapter does not support 'before' execution")

    def after(self, ctx, task, flag: str = None, **kwargs):
        raise NotImplementedError("This adapter does not support 'after' execution")

    def during(self, ctx, task, flag: str = None, **kwargs):
        raise NotImplementedError("This adapter does not support 'during' execution")
    

class MytoDecoAdapter:
    _before : list[callable] = []
    _after : list[callable] = []
    _during : list[callable] = []

    def addBefore(self, func: callable):
        self._before.append(func)

    def addAfter(self, func: callable):
        self._after.append(func)

    def addDuring(self, func: callable):
        self._during.append(func)

    def before(self, ctx, task, flag: str = None, **kwargs):
        for func in self._before:
            func(ctx, task, flag, **kwargs)

    def after(self, ctx, task, flag: str = None, **kwargs):
        for func in self._after:
            func(ctx, task, flag, **kwargs)

    def during(self, ctx, task, flag: str = None, **kwargs):
        for func in self._during:
            func(ctx, task, flag, **kwargs)