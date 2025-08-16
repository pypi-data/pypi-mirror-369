from dataclasses import field, dataclass
import re

from myto.base.adapter import MytoAdapter


@dataclass
class MytoCtx:
    """
    A stack-based context manager for storing and managing key-value pairs across different execution levels.
    
    This class provides a hierarchical context system where you can push/pop context levels,
    filter keys using exact matches or regex patterns, and manage context state across
    different execution scopes. Context levels can optionally be named for easier reference.
    
    Attributes:
        meta (dict): Metadata dictionary for storing additional information.
    """
    runner : object
    meta : dict = field(default_factory=dict)

    @property
    def adapters(self) -> list[MytoAdapter]:
        return self.runner.ctxAdapters

    @property
    def named(self) -> bool:
        """
        Check if the current top-level context has a name.
        
        Returns:
            bool: True if the current context level has a name, False otherwise.
        """
        return bool(self._internal_stack_names[-1])

    def rename(self, name: str):
        """
        Rename the current top-level context.
        
        Args:
            name (str): The new name for the current context level.
            
        Raises:
            ValueError: If the current context is unnamed or if the name already exists.
        """
        if not self.named:
            raise ValueError("Cannot rename unnamed context")
        if name in self._internal_stack_names:
            raise ValueError(f"Context with name '{name}' already exists")

        self._internal_stack_names[-1] = name

    def getNamed(self, name : str):
        """
        Get the context dictionary for a named context level.
        
        Args:
            name (str): The name of the context level to retrieve.
            
        Returns:
            dict: The context dictionary for the specified named level.
            
        Raises:
            ValueError: If the current context is unnamed or if the named context doesn't exist.
        """
        if not self.named:
            raise ValueError("Cannot get name of unnamed context")
        index = self._internal_stack_names.index(name)
        return self._internal_stack[index]

    @property
    def stackCtx(self):
        """
        Get the current top-level context dictionary from the stack.
        
        Returns:
            dict: The dictionary at the top of the internal stack.
        """
        return self._internal_stack[-1]

    def __post_init__(self):
        """Initialize the internal stack with an empty dictionary as the base level and empty names list."""
        self._internal_stack : list[dict] = [{}]
        self._internal_stack_names : list[str] = [None]

    def flush(self):
        """Clear all key-value pairs from the current stack context."""
        self.stackCtx.clear()

    def push(self, name: str = None):
        """
        Push a new empty context level onto the stack.
        
        This creates a new scope for context variables, allowing you to isolate
        context changes within a specific execution block. The context level can
        optionally be given a name for easier reference.
        
        Args:
            name (str, optional): An optional name for the new context level.
                                Must be unique among existing named contexts.
                                
        Raises:
            ValueError: If a context with the given name already exists.
        """
        
        if name and name in self._internal_stack_names:
            raise ValueError(f"Context with name '{name}' already exists")
        self._internal_stack.append({})
        self._internal_stack_names.append(name)

    def pop(self) -> dict:
        """
        Pop the top context level from the stack and return it.
        
        This removes both the context dictionary and its associated name (if any)
        from their respective stacks.
        
        Returns:
            dict: The context dictionary that was removed from the top of the stack.
            
        Raises:
            IndexError: If attempting to pop when only the base level remains.
        """
        self._internal_stack_names.pop()
        return self._internal_stack.pop()
    
    
    def filterKey(self, key: str):
        """
        Filter the current stack context for keys that match the given key exactly or by regex.
        
        Args:
            key (str): The key to match exactly, or a regex pattern to match against keys.
            
        Returns:
            dict: A dictionary containing all matching key-value pairs.
        """
        matched = {}
        for k, v in self.stackCtx.items():
            if k == key or re.match(key, k):
                matched[k] = v
        return matched

    def filterKeys(self, keys: list[str]) -> dict:
        """
        Filter the current stack context for multiple keys using exact match or regex.
        
        Args:
            keys (list[str]): List of keys to filter for. Each can be an exact match or regex pattern.
            
        Returns:
            dict: A dictionary containing all matching key-value pairs from all specified keys.
        """
        filtered = {}
        for k in keys:
            result = self.filterKey(k)
            filtered.update(result)
        return filtered

    def restack(self, keys : list[str] = None):
        """
        Replace the current stack level with a new one, optionally preserving specified keys.
        
        This method pops the current context, pushes a new empty context, and optionally
        restores filtered key-value pairs to the new context level. The new context level
        will be unnamed.
        
        Args:
            keys (list[str], optional): List of keys to preserve from the old context.
                                      If None, no keys are preserved.
        """
        if keys:
            currentFiltered = self.filterKeys(keys)
        
        self.pop()
        self.push()

        if keys:
            self.stackCtx.update(currentFiltered)

    def rebase(self, keys : list[str] = None):
        """
        Merge the current stack level down to the previous level, optionally filtering keys.
        
        This method pops the current context and merges specified keys (or none if keys=None)
        into the previous stack level.
        
        Args:
            keys (list[str], optional): List of keys to merge down to the previous level.
                                      If None, no keys are merged.
                                      
        Raises:
            IndexError: If there are fewer than two stack levels (cannot merge down from base level).
        """
        if len(self._internal_stack) < 2:
            raise IndexError("Cannot restack with less than two stack levels")

        currentFiltered = self.filterKeys(keys) if keys else {}
        self.pop()
        self.stackCtx.update(currentFiltered)
