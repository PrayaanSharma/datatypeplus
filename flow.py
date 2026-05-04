import functools
import itertools
import math
from typing import Any, Dict, List, Tuple, Union, Iterator, Optional
from collections.abc import Mapping

def info():
    print("""This is a library called 'datatypeplus' that provides advanced data structures:
- FlexString: A mutable string with list-like and string-like methods.
- NList: A multi-dimensional container with labeled axes and advanced indexing.
- EvolveList and EvolveElement: Reactive lists with condition-based element updates.
It was written in October 2025 by Prayaan Sharma.
This version was made on November 2, 2025.
This is version 1.1.1 of the library.""")

class FlexString:
    """
    A fully mutable string with list-like and string-like methods.
    """
    
    def __init__(self, initial=""):
        if not isinstance(initial, (str, FlexString)):
            raise TypeError(f"Initial value must be str or FlexString, not {type(initial).__name__}")
        self._chars = list(str(initial))
    
    # ---- Core Protocols ----
    def __str__(self):
        return "".join(self._chars)
    
    def __repr__(self):
        return f'FlexString("{str(self)}")'
    
    def __len__(self):
        return len(self._chars)
    
    def __iter__(self):
        return iter(self._chars)
    
    def __contains__(self, item):
        if isinstance(item, str):
            return item in str(self)
        return item in self._chars
    
    def __eq__(self, other):
        if isinstance(other, FlexString):
            return self._chars == other._chars
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __add__(self, other):
        result = self.copy()
        if isinstance(other, (str, FlexString)):
            result.extend(str(other))
        else:
            return NotImplemented
        return result
    
    def __radd__(self, other):
        if isinstance(other, str):
            result = FlexString(other)
            result.extend(self)
            return result
        return NotImplemented
    
    def __mul__(self, n):
        if not isinstance(n, int):
            return NotImplemented
        result = FlexString()
        result._chars = self._chars * n
        return result
    
    def __rmul__(self, n):
        return self.__mul__(n)
    
    # ---- Indexing and Slicing ----
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return FlexString("".join(self._chars[idx]))
        return self._chars[idx]
    
    def __setitem__(self, idx, value):
        if not isinstance(value, str):
            raise TypeError("Value must be string")
            
        if isinstance(idx, slice):
            # Handle slice assignment properly
            chars_to_insert = list(value)
            if idx.step is None or idx.step == 1:
                # Simple case: replace contiguous slice
                start = idx.start if idx.start is not None else 0
                stop = idx.stop if idx.stop is not None else len(self)
                start = start if start >= 0 else len(self) + start
                stop = stop if stop >= 0 else len(self) + stop
                
                # Replace the slice
                self._chars[start:stop] = chars_to_insert
            else:
                # Complex case: extended slice, must match exact size
                indices = range(len(self))[idx]
                if len(indices) != len(chars_to_insert):
                    raise ValueError(f"attempt to assign sequence of size {len(chars_to_insert)} to extended slice of size {len(indices)}")
                for i, char in zip(indices, chars_to_insert):
                    self._chars[i] = char
        else:
            # Single character assignment
            if len(value) != 1:
                raise ValueError("Single index assignment requires single character")
            idx = idx if idx >= 0 else len(self) + idx
            self._chars[idx] = value
    
    def __delitem__(self, idx):
        del self._chars[idx]
    
    # ---- List-like Methods ----
    def append(self, value):
        """Append a string to the end."""
        if not isinstance(value, str):
            raise TypeError("Can only append strings")
        self._chars.extend(list(value))
    
    def extend(self, iterable):
        """Extend with characters from any iterable of strings."""
        for item in iterable:
            if not isinstance(item, str):
                raise TypeError("All items must be strings")
            self._chars.extend(list(item))
    
    def insert(self, index, value):
        """Insert a string at the given index."""
        if not isinstance(value, str):
            raise TypeError("Can only insert strings")
        
        # Handle negative indices
        if index < 0:
            index = max(0, len(self) + index)
        index = min(index, len(self))  # Don't go beyond end
        
        # Insert all characters at once
        self._chars[index:index] = list(value)
    
    def remove(self, value):
        """Remove first occurrence of substring."""
        if not isinstance(value, str):
            raise TypeError("Can only remove strings")
        
        s = str(self)
        pos = s.find(value)
        if pos == -1:
            raise ValueError("Substring not found")
        
        del self._chars[pos:pos+len(value)]
    
    def pop(self, index=-1):
        """Remove and return character at index."""
        if not self._chars:
            raise IndexError("pop from empty FlexString")
        return self._chars.pop(index)
    
    def clear(self):
        """Remove all characters."""
        self._chars.clear()
    
    def reverse(self):
        """Reverse the string in-place."""
        self._chars.reverse()
    
    def count(self, sub, start=0, end=None):
        """Count occurrences of substring."""
        return str(self).count(sub, start, end or len(self))
    
    def index(self, sub, start=0, end=None):
        """Find first occurrence of substring."""
        result = self.find(sub, start, end)
        if result == -1:
            raise ValueError("Substring not found")
        return result
    
    # ---- String Methods (In-place) ----
    def lower(self):
        """Convert to lowercase in-place."""
        for i in range(len(self._chars)):
            self._chars[i] = self._chars[i].lower()
    
    def upper(self):
        """Convert to uppercase in-place."""
        for i in range(len(self._chars)):
            self._chars[i] = self._chars[i].upper()
    
    def capitalize(self):
        """Capitalize the string in-place."""
        if self._chars:
            self._chars[0] = self._chars[0].upper()
            for i in range(1, len(self._chars)):
                self._chars[i] = self._chars[i].lower()
    
    def title(self):
        """Title-case the string in-place."""
        if not self._chars:
            return
        
        title_next = True
        for i, char in enumerate(self._chars):
            if char.isalpha():
                if title_next:
                    self._chars[i] = char.upper()
                    title_next = False
                else:
                    self._chars[i] = char.lower()
            else:
                title_next = True
    
    def swapcase(self):
        """Swap case of all characters in-place."""
        for i in range(len(self._chars)):
            self._chars[i] = self._chars[i].swapcase()
    
    def replace(self, old, new, count=-1, case_sensitive=True):
        """Replace occurrences of old with new in-place."""
        s = str(self)
        if not case_sensitive:
            # Case-insensitive replacement
            temp = s.lower()
            old_lower = old.lower()
            result = []
            i = 0
            replacements = 0
            
            while i < len(s) and (count == -1 or replacements < count):
                if temp[i:i+len(old_lower)] == old_lower:
                    result.append(new)
                    i += len(old_lower)
                    replacements += 1
                else:
                    result.append(s[i])
                    i += 1
            result.append(s[i:])
            self._chars = list(''.join(result))
        else:
            # Case-sensitive replacement
            s = s.replace(old, new, count)
            self._chars = list(s)
    
    def strip(self, chars=None):
        """Strip characters from both ends in-place."""
        s = str(self).strip(chars)
        self._chars = list(s)
    
    def lstrip(self, chars=None):
        """Strip characters from left end in-place."""
        s = str(self).lstrip(chars)
        self._chars = list(s)
    
    def rstrip(self, chars=None):
        """Strip characters from right end in-place."""
        s = str(self).rstrip(chars)
        self._chars = list(s)
    
    # ---- String Methods (Read-only) ----
    def find(self, sub, start=0, end=None):
        """Find substring and return index, or -1 if not found."""
        return str(self).find(sub, start, end or len(self))
    
    def rfind(self, sub, start=0, end=None):
        """Find substring from right and return index, or -1 if not found."""
        return str(self).rfind(sub, start, end or len(self))
    
    def startswith(self, prefix, start=0, end=None):
        """Check if string starts with prefix."""
        return str(self).startswith(prefix, start, end or len(self))
    
    def endswith(self, suffix, start=0, end=None):
        """Check if string ends with suffix."""
        return str(self).endswith(suffix, start, end or len(self))
    
    # ---- Utility Methods ----
    def copy(self):
        """Return a shallow copy."""
        return FlexString(str(self))
    
    def to_str(self):
        """Convert to regular string (alias for str(self))."""
        return str(self)
    
    def to_list(self):
        """Return as list of characters."""
        return self._chars.copy()

class NList:
    """
    A structured, multi-dimensional container with labeled axes and advanced indexing.
    
    Features:
    - Dynamic axis management
    - Advanced slicing and indexing
    - Mathematical operations
    - Sparse data support
    - SQL-like querying
    - Pandas-like functionality in pure Python
    
    Example:
        >>> nl = NList()
        >>> nl.add_axis("Person", ["Alice", "Bob"])
        >>> nl.add_axis("Month", ["Jan", "Feb"])
        >>> nl["Alice", "Jan"] = 100
        >>> print(nl["Alice", "Jan"])  # 100
    """
    def __init__(self, axes: Dict[str, List[Any]], default=None):
        self.axis_names = list(axes.keys())
        self.label_to_idx = [
            {label: i for i, label in enumerate(labels)} 
            for labels in axes.values()
        ]
        self.markers = [list(labels) for labels in axes.values()]
        self.shape = tuple(len(m) for m in self.markers)
        
        # Calculate strides
        self.strides = []
        for i in range(len(self.shape)):
            stride = 1
            for j in range(i + 1, len(self.shape)):
                stride *= self.shape[j]
            self.strides.append(stride)
            
        total_size = 1
        for dim in self.shape:
            total_size *= dim
        self.data = [default] * total_size

    def _resolve_key(self, axis_idx, key):
        """Converts a label, integer, or slice into a list of integer indices."""
        axis_len = self.shape[axis_idx]
        
        # Handle Slices (e.g., nl["Alice", "Jan":"Mar"])
        if isinstance(key, slice):
            # Resolve start/stop labels to integers if they aren't None or ints
            start = self.label_to_idx[axis_idx].get(key.start, key.start)
            stop = self.label_to_idx[axis_idx].get(key.stop, key.stop)
            return range(*slice(start, stop, key.step).indices(axis_len))
        
        # Handle individual labels or integers
        if key in self.label_to_idx[axis_idx]:
            return [self.label_to_idx[axis_idx][key]]
        if isinstance(key, int):
            if -axis_len <= key < axis_len:
                return [key % axis_len]
        
        raise KeyError(f"Key '{key}' not found in axis '{self.axis_names[axis_idx]}'")

    def __getitem__(self, keys):
        # Normalize single key to tuple
        if not isinstance(keys, tuple):
            keys = (keys,)
            
        if len(keys) != len(self.axis_names):
            raise ValueError(f"Expected {len(self.axis_names)} keys, got {len(keys)}")

        # Step 1: Get lists of integer indices for every axis
        indices_per_axis = [self._resolve_key(i, k) for i, k in enumerate(keys)]
        
        # Step 2: Calculate flat positions
        # Cartesian product gives all combinations of indices
        flat_positions = []
        for combo in itertools.product(*indices_per_axis):
            pos = sum(idx * stride for idx, stride in zip(combo, self.strides))
            flat_positions.append(self.data[pos])
            
        # If the user asked for a single point, return the value. 
        # If they used slices, return a list of results.
        is_single_point = all(not isinstance(k, slice) for k in keys)
        return flat_positions[0] if is_single_point else flat_positions

    def __setitem__(self, keys, value):
        if not isinstance(keys, tuple):
            keys = (keys,)
            
        indices_per_axis = [self._resolve_key(i, k) for i, k in enumerate(keys)]
        flat_positions = [
            sum(idx * stride for idx, stride in zip(combo, self.strides))
            for combo in itertools.product(*indices_per_axis)
        ]
        
        if len(flat_positions) > 1 and not isinstance(value, (list, tuple)):
            # Broad-casting a single value to multiple cells
            for pos in flat_positions:
                self.data[pos] = value
        else:
            for pos in flat_positions:
                self.data[pos] = value

    def __repr__(self):
        return f"NList(shape={self.shape}, axes={self.axis_names})"


class EvolveList:
    """
    Reactive list where elements can have conditions and actions that trigger when conditions change.
    """

    def __init__(self, data=None):
        self.data = list(data) if data else []
        # element_index -> [(condition, action, last_state)]
        self._element_conditions = {}
        self._in_update = False

    def __getitem__(self, index):
        if index < 0:
            index = len(self.data) + index
        return EvolveElement(self, index)

    def __setitem__(self, index, value):
        if self.data[index] == value:
            return  # no change, no trigger
        self.data[index] = value
        if not self._in_update:
            self._check_conditions_state_based()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return f"EvolveList({self.data})"

    # ------------------------------------------------
    # Basic list operations
    # ------------------------------------------------
    def append(self, value):
        self.data.append(value)
        self._element_conditions.setdefault(len(self.data) - 1, [])
        if not self._in_update:
            self._check_conditions_state_based()

    def insert(self, index, value):
        self.data.insert(index, value)
        # shift all condition indices
        new_cond = {}
        for i, conds in self._element_conditions.items():
            new_cond[i + 1 if i >= index else i] = [(c, a, False) for c, a, _ in conds]
        self._element_conditions = new_cond
        self._element_conditions.setdefault(index, [])
        if not self._in_update:
            self._check_conditions_state_based()

    def pop(self, index=-1):
        value = self.data.pop(index)
        # shift conditions
        new_cond = {}
        for i, conds in self._element_conditions.items():
            if i == index:
                continue
            new_cond[i - 1 if i > index else i] = [(c, a, False) for c, a, _ in conds]
        self._element_conditions = new_cond
        if not self._in_update:
            self._check_conditions_state_based()
        return value

    def clear(self):
        self.data.clear()
        self._element_conditions.clear()

    # ------------------------------------------------
    # Condition management
    # ------------------------------------------------
    def add_condition(self, element_index, condition, action):
        """Add a condition/action pair to a specific element."""
        if element_index not in self._element_conditions:
            self._element_conditions[element_index] = []
        self._element_conditions[element_index].append((condition, action, False))

    def remove_conditions(self, element_index):
        """Remove all conditions from one element."""
        if element_index in self._element_conditions:
            del self._element_conditions[element_index]

    def clear_all_conditions(self):
        """Clear every condition in the list."""
        self._element_conditions.clear()

    # ------------------------------------------------
    # Reactive evaluation
    # ------------------------------------------------
    def _check_conditions_state_based(self):
        if self._in_update:
            return
        self._in_update = True
        try:
            for idx, conds in list(self._element_conditions.items()):
                new_conds = []
                for condition, action, last_state in conds:
                    try:
                        current_state = condition.check()
                        if current_state and not last_state:
                            self._execute_action(action)
                        new_conds.append((condition, action, current_state))
                    except Exception:
                        continue
                self._element_conditions[idx] = new_conds
        finally:
            self._in_update = False

    def _execute_action(self, action):
        try:
            if callable(action):
                action()
            else:
                print(action)
        except Exception as e:
            print(f"Action error: {e}")

    def check(self):
        """Manually trigger condition checking."""
        self._check_conditions_state_based()


class EvolveElement:
    """Represents a single element in an EvolveList that can have conditions."""

    def __init__(self, evolve_list, index):
        self.evolve_list = evolve_list
        self.index = index

    @property
    def value(self):
        return self.evolve_list.data[self.index]

    @value.setter
    def value(self, new_value):
        self.evolve_list[self.index] = new_value

    def when(self, condition):
        """Start defining a reactive condition or combined condition."""
        if not isinstance(condition, _Condition):
            raise TypeError("Condition must be a _Condition instance or combination")
        return _ConditionBuilder(self.evolve_list, self.index, condition)

    def set_condition(self, condition, action):
        """Attach a condition and action directly."""
        self.evolve_list.add_condition(self.index, condition, action)
        return self

    # Comparison overrides → return _Condition objects
    def __eq__(self, other):
        return _Condition(self.evolve_list, lambda: self.value == getattr(other, "value", other))

    def __ne__(self, other):
        return _Condition(self.evolve_list, lambda: self.value != getattr(other, "value", other))

    def __lt__(self, other):
        return _Condition(self.evolve_list, lambda: self.value < getattr(other, "value", other))

    def __le__(self, other):
        return _Condition(self.evolve_list, lambda: self.value <= getattr(other, "value", other))

    def __gt__(self, other):
        return _Condition(self.evolve_list, lambda: self.value > getattr(other, "value", other))

    def __ge__(self, other):
        return _Condition(self.evolve_list, lambda: self.value >= getattr(other, "value", other))

    def __repr__(self):
        return f"EvolveElement({self.value} @ {self.index})"


class _ConditionBuilder:
    """Helper for fluent condition building like element.when(...).do(...)."""

    def __init__(self, evolve_list, element_index, condition):
        self.evolve_list = evolve_list
        self.element_index = element_index
        self.condition = condition

    def do(self, action, *args, **kwargs):
        """Attach an action to the condition."""
        if args or kwargs:
            wrapped_action = lambda: action(*args, **kwargs)
        else:
            wrapped_action = action
        self.evolve_list.add_condition(self.element_index, self.condition, wrapped_action)
        return self.evolve_list[self.element_index]

    def print(self, message):
        """Quick shorthand to print something when triggered."""
        return self.do(lambda: print(message))

    def set_value(self, target_index, value):
        """Set another element's value when triggered."""
        return self.do(lambda: self.evolve_list.__setitem__(target_index, value))


class _Condition:
    """Represents a condition that can be checked or combined."""

    def __init__(self, evolve_list, func):
        self.evolve_list = evolve_list
        self.func = func

    def check(self):
        try:
            return bool(self.func())
        except Exception:
            return False

    # Logical combination support
    def __and__(self, other):
        return _Condition(self.evolve_list, lambda: self.check() and other.check())

    def __or__(self, other):
        return _Condition(self.evolve_list, lambda: self.check() or other.check())

    def __invert__(self):
        return _Condition(self.evolve_list, lambda: not self.check())
