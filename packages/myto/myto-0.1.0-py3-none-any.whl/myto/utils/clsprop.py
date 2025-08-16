class classproperty:
    """
    A descriptor that creates a property at the class level.
    
    Usage:
        class MyClass:
            _value = "default"
            
            @classproperty
            def value(cls):
                return cls._value
                
            @value.setter
            def value(cls, val):
                cls._value = val
    """
    
    def __init__(self, fget=None, fset=None):
        self.fget = fget
        self.fset = fset
    
    def __get__(self, instance, owner):
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(owner)
    
    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        return self.fset(type(instance), value)
    
    def setter(self, fset):
        """Create a new classproperty with a setter."""
        return type(self)(self.fget, fset)