import json
import re
import functools
import itertools
from typing import Any, Dict, List, Tuple, Union, Iterator, Optional, Callable, Set
from collections.abc import Mapping

# ==========================================
# 0. Reactive Primitive Engine (Signal/Computed/Effect)
# ==========================================

_CURRENT_SUBSCRIBER = None


class Signal:
    """Fine-grained reactive state primitive."""
    def __init__(self, value: Any = None):
        self._value = value
        self._subscribers: Set[Callable[[], None]] = set()

    def get(self) -> Any:
        if _CURRENT_SUBSCRIBER is not None:
            self._subscribers.add(_CURRENT_SUBSCRIBER)
        return self._value

    def set(self, value: Any) -> None:
        if self._value != value:
            self._value = value
            self.notify()

    def notify(self) -> None:
        for sub in list(self._subscribers):
            sub()

    @property
    def value(self) -> Any:
        return self.get()

    @value.setter
    def value(self, val: Any) -> None:
        self.set(val)

    def __repr__(self):
        return f"Signal({self._value!r})"


class Computed:
    """Reactive value derived from other Signals or Computed primitives."""
    def __init__(self, fn: Callable[[], Any]):
        self._fn = fn
        self._value = None
        self._dirty = True
        self._subscribers: Set[Callable[[], None]] = set()

        def _on_dependency_change():
            self._dirty = True
            self.notify()

        self._dependency_callback = _on_dependency_change
        self._evaluate()

    def _evaluate(self):
        global _CURRENT_SUBSCRIBER
        prev_subscriber = _CURRENT_SUBSCRIBER
        _CURRENT_SUBSCRIBER = self._dependency_callback
        try:
            self._value = self._fn()
            self._dirty = False
        finally:
            _CURRENT_SUBSCRIBER = prev_subscriber

    def get(self) -> Any:
        if self._dirty:
            self._evaluate()
        if _CURRENT_SUBSCRIBER is not None:
            self._subscribers.add(_CURRENT_SUBSCRIBER)
        return self._value

    def notify(self) -> None:
        for sub in list(self._subscribers):
            sub()

    @property
    def value(self) -> Any:
        return self.get()

    def __repr__(self):
        return f"Computed({self.get()!r})"


class Effect:
    """Reactive effect that runs whenever its dependencies change."""
    def __init__(self, fn: Callable[[], None]):
        self._fn = fn
        self._active = True
        self.run()

    def run(self) -> None:
        if not self._active:
            return
        global _CURRENT_SUBSCRIBER
        prev_subscriber = _CURRENT_SUBSCRIBER
        _CURRENT_SUBSCRIBER = self.run
        try:
            self._fn()
        finally:
            _CURRENT_SUBSCRIBER = prev_subscriber

    def dispose(self) -> None:
        self._active = False


def info():
    """Prints metadata about datatypeplus library."""
    print("""datatypeplus v2.0.0 - Advanced Data Structures and Reactive Containers
    
Includes:
- FlexString: Fluent, mutable string with regex, case conversions, and parsing.
- NList: Multi-dimensional sparse container with sub-grid slicing, dynamic axes, and aggregations.
- EvolveList & EvolveElement: Reactive list with condition triggers, batching, computed elements, and event hooks.
- FlexDict: Dot-access dictionary with auto-vivification, flattening, and deep merging.
- EvolveDict: Reactive dictionary with key-level conditions and event hooks.
- Signal, Computed, Effect: Standalone fine-grained reactive engine.
- FlexTree: Hierarchical tree container with path navigation and traversal.

Author: Prayaan Sharma
License: MIT""")


# ==========================================
# 1. FlexString
# ==========================================

class FlexString:
    """A fully mutable string with fluent chaining, case conversions, regex, and parsing capabilities."""

    def __init__(self, initial=""):
        if not isinstance(initial, (str, FlexString)):
            raise TypeError(f"Initial value must be str or FlexString, not {type(initial).__name__}")
        self._chars = list(str(initial))

    # Core Protocols
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
        res = self.__eq__(other)
        return not res if res is not NotImplemented else NotImplemented

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

    # Indexing and Slicing
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return FlexString("".join(self._chars[idx]))
        return self._chars[idx]

    def __setitem__(self, idx, value):
        if not isinstance(value, str):
            raise TypeError("Value must be string")

        if isinstance(idx, slice):
            chars_to_insert = list(value)
            if idx.step is None or idx.step == 1:
                start = idx.start if idx.start is not None else 0
                stop = idx.stop if idx.stop is not None else len(self)
                start = start if start >= 0 else len(self) + start
                stop = stop if stop >= 0 else len(self) + stop
                self._chars[start:stop] = chars_to_insert
            else:
                indices = range(len(self))[idx]
                if len(indices) != len(chars_to_insert):
                    raise ValueError("assignment length mismatch")
                for i, char in zip(indices, chars_to_insert):
                    self._chars[i] = char
        else:
            if len(value) != 1:
                raise ValueError("Single index assignment requires single character")
            idx = idx if idx >= 0 else len(self) + idx
            self._chars[idx] = value

    def __delitem__(self, idx):
        del self._chars[idx]

    # In-place List-like Methods
    def append(self, value):
        if not isinstance(value, str):
            raise TypeError("Can only append strings")
        self._chars.extend(list(value))
        return self

    def extend(self, iterable):
        for item in iterable:
            if not isinstance(item, str):
                raise TypeError("All items must be strings")
            self._chars.extend(list(item))
        return self

    def insert(self, index, value):
        if not isinstance(value, str):
            raise TypeError("Can only insert strings")
        if index < 0:
            index = max(0, len(self) + index)
        index = min(index, len(self))
        self._chars[index:index] = list(value)
        return self

    def remove(self, value):
        if not isinstance(value, str):
            raise TypeError("Can only remove strings")
        s = str(self)
        pos = s.find(value)
        if pos == -1:
            raise ValueError("Substring not found")
        del self._chars[pos:pos+len(value)]
        return self

    def pop(self, index=-1):
        if not self._chars:
            raise IndexError("pop from empty FlexString")
        return self._chars.pop(index)

    def clear(self):
        self._chars.clear()
        return self

    def reverse(self):
        self._chars.reverse()
        return self

    def count(self, sub, start=0, end=None):
        return str(self).count(sub, start, end or len(self))

    def index(self, sub, start=0, end=None):
        result = self.find(sub, start, end)
        if result == -1:
            raise ValueError("Substring not found")
        return result

    # In-place Transformation Methods
    def lower(self):
        self._chars = [c.lower() for c in self._chars]
        return self

    def upper(self):
        self._chars = [c.upper() for c in self._chars]
        return self

    def capitalize(self):
        if self._chars:
            self._chars[0] = self._chars[0].upper()
            for i in range(1, len(self._chars)):
                self._chars[i] = self._chars[i].lower()
        return self

    def title(self):
        s = str(self).title()
        self._chars = list(s)
        return self

    def to_title(self):
        """Alias for title() to match to_snake/to_camel naming patterns."""
        return self.title()

    def swapcase(self):
        self._chars = [c.swapcase() for c in self._chars]
        return self

    def replace(self, old, new, count=-1, case_sensitive=True):
        s = str(self)
        if not case_sensitive:
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
            s = s.replace(old, new, count)
            self._chars = list(s)
        return self

    def strip(self, chars=None):
        s = str(self).strip(chars)
        self._chars = list(s)
        return self

    def lstrip(self, chars=None):
        s = str(self).lstrip(chars)
        self._chars = list(s)
        return self

    def rstrip(self, chars=None):
        s = str(self).rstrip(chars)
        self._chars = list(s)
        return self

    # Advanced Case Conversions
    def to_snake(self):
        s = str(self)
        s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
        s = re.sub(r'[^a-zA-Z0-9]+', '_', s)
        s = re.sub(r'_+', '_', s).strip('_').lower()
        self._chars = list(s)
        return self

    def to_camel(self):
        self.to_snake()
        parts = str(self).split('_')
        if parts:
            s = parts[0] + "".join(p.capitalize() for p in parts[1:])
            self._chars = list(s)
        return self

    def to_pascal(self):
        self.to_snake()
        parts = str(self).split('_')
        if parts:
            s = "".join(p.capitalize() for p in parts)
            self._chars = list(s)
        return self

    def to_kebab(self):
        self.to_snake()
        s = str(self).replace('_', '-')
        self._chars = list(s)
        return self

    def slugify(self):
        self.to_snake()
        s = str(self).replace('_', '-')
        self._chars = list(s)
        return self

    # Regex & Formatting
    def regex_replace(self, pattern, repl, flags=0):
        s = re.sub(pattern, repl, str(self), flags=flags)
        self._chars = list(s)
        return self

    def extract(self, pattern, flags=0):
        return re.findall(pattern, str(self), flags=flags)

    def split(self, delimiter=None, maxsplit=-1):
        s = str(self)
        parts = s.split(delimiter, maxsplit)
        return [FlexString(p) for p in parts]

    def clean_whitespace(self):
        s = re.sub(r'\s+', ' ', str(self)).strip()
        self._chars = list(s)
        return self

    def truncate(self, length, suffix="..."):
        if len(self._chars) > length:
            keep = max(0, length - len(suffix))
            self._chars = self._chars[:keep] + list(suffix)
        return self

    def format_map(self, mapping):
        s = str(self).format_map(mapping)
        self._chars = list(s)
        return self

    # Read-only and Parsing Methods
    def find(self, sub, start=0, end=None):
        return str(self).find(sub, start, end or len(self))

    def rfind(self, sub, start=0, end=None):
        return str(self).rfind(sub, start, end or len(self))

    def startswith(self, prefix, start=0, end=None):
        return str(self).startswith(prefix, start, end or len(self))

    def endswith(self, suffix, start=0, end=None):
        return str(self).endswith(suffix, start, end or len(self))

    def to_int(self, default=None):
        try:
            return int(str(self))
        except ValueError:
            return default

    def to_float(self, default=None):
        try:
            return float(str(self))
        except ValueError:
            return default

    def to_json(self):
        return json.loads(str(self))

    def copy(self):
        return FlexString(str(self))

    def to_str(self):
        return str(self)

    def to_list(self):
        return self._chars.copy()


# ==========================================
# 2. NList
# ==========================================

class NList:
    """
    A multi-dimensional sparse grid with labeled axes, sub-grid slicing,
    dynamic axis management, aggregations, and export capabilities.
    """
    def __init__(self, axes: Dict[str, List[Any]] = None, default=None):
        axes = axes or {}
        self.axis_names: List[str] = list(axes.keys())
        self.markers: List[List[Any]] = [list(labels) for labels in axes.values()]
        self.label_to_idx: List[Dict[Any, int]] = [
            {label: i for i, label in enumerate(labels)}
            for labels in self.markers
        ]
        self.default = default
        self._data: Dict[Tuple[int, ...], Any] = {}

    @property
    def shape(self) -> Tuple[int, ...]:
        return tuple(len(m) for m in self.markers)

    def _resolve_key(self, axis_idx: int, key: Any) -> Tuple[List[int], List[Any], bool]:
        axis_len = len(self.markers[axis_idx])
        axis_labels = self.markers[axis_idx]

        if key == slice(None):
            return list(range(axis_len)), axis_labels.copy(), True

        if isinstance(key, slice):
            start = self.label_to_idx[axis_idx].get(key.start, key.start) if key.start is not None else 0
            stop = self.label_to_idx[axis_idx].get(key.stop, key.stop) if key.stop is not None else axis_len
            if isinstance(stop, int) and key.stop in self.label_to_idx[axis_idx]:
                stop += 1
            step = key.step or 1
            indices = list(range(start, stop, step))
            sub_labels = [axis_labels[i] for i in indices if 0 <= i < axis_len]
            return indices, sub_labels, True

        if isinstance(key, list):
            indices = []
            sub_labels = []
            for k in key:
                idx = self.label_to_idx[axis_idx].get(k, k if isinstance(k, int) else None)
                if idx is not None and 0 <= idx < axis_len:
                    indices.append(idx)
                    sub_labels.append(axis_labels[idx])
            return indices, sub_labels, True

        idx = self.label_to_idx[axis_idx].get(key, key if isinstance(key, int) else None)
        if idx is not None and -axis_len <= idx < axis_len:
            idx = idx % axis_len
            return [idx], [axis_labels[idx]], False

        raise KeyError(f"Key '{key}' not found in axis '{self.axis_names[axis_idx]}'")

    def __getitem__(self, keys):
        if not isinstance(keys, tuple):
            keys = (keys,)

        if len(keys) != len(self.axis_names):
            raise ValueError(f"Expected {len(self.axis_names)} keys, got {len(keys)}")

        resolved = [self._resolve_key(i, k) for i, k in enumerate(keys)]
        indices_per_axis = [r[0] for r in resolved]
        sub_labels_per_axis = [r[1] for r in resolved]
        is_slice = any(r[2] for r in resolved)

        if not is_slice:
            coord = tuple(indices_per_axis[i][0] for i in range(len(keys)))
            return self._data.get(coord, self.default)

        sub_axes = {
            self.axis_names[i]: sub_labels_per_axis[i]
            for i in range(len(self.axis_names))
        }
        sub_nlist = NList(axes=sub_axes, default=self.default)

        for combo in itertools.product(*[range(len(ind)) for ind in indices_per_axis]):
            orig_coord = tuple(indices_per_axis[dim][combo[dim]] for dim in range(len(keys)))
            if orig_coord in self._data:
                sub_nlist._data[combo] = self._data[orig_coord]

        return sub_nlist

    def __setitem__(self, keys, value):
        if not isinstance(keys, tuple):
            keys = (keys,)

        if len(keys) != len(self.axis_names):
            raise ValueError(f"Expected {len(self.axis_names)} keys, got {len(keys)}")

        indices_per_axis = [self._resolve_key(i, k)[0] for i, k in enumerate(keys)]
        coords = list(itertools.product(*indices_per_axis))

        if isinstance(value, NList):
            for idx, c in enumerate(coords):
                sub_c = tuple(range(len(c)))
                if sub_c in value._data:
                    self._data[c] = value._data[sub_c]
        else:
            for c in coords:
                self._data[c] = value

    def set(self, *markers, value):
        self[markers] = value

    def get(self, *markers):
        return self[markers]

    # Dynamic Axis Operations
    def add_axis(self, name: str, labels: List[Any], default_value=None):
        if name in self.axis_names:
            raise ValueError(f"Axis '{name}' already exists.")
        self.axis_names.append(name)
        self.markers.append(list(labels))
        self.label_to_idx.append({label: i for i, label in enumerate(labels)})

        new_data = {}
        for coord, val in self._data.items():
            new_data[coord + (0,)] = val
        self._data = new_data
        return self

    def drop_axis(self, name: str):
        if name not in self.axis_names:
            raise KeyError(f"Axis '{name}' not found.")
        idx = self.axis_names.index(name)
        del self.axis_names[idx]
        del self.markers[idx]
        del self.label_to_idx[idx]

        new_data = {}
        for coord, val in self._data.items():
            new_coord = coord[:idx] + coord[idx+1:]
            new_data[new_coord] = val
        self._data = new_data
        return self

    def rename_axis(self, old_name: str, new_name: str):
        idx = self.axis_names.index(old_name)
        self.axis_names[idx] = new_name
        return self

    def transpose(self, *axis_order):
        if len(axis_order) != len(self.axis_names):
            raise ValueError("Transpose order must match number of axes")
        indices = [self.axis_names.index(name) for name in axis_order]

        self.axis_names = [self.axis_names[i] for i in indices]
        self.markers = [self.markers[i] for i in indices]
        self.label_to_idx = [self.label_to_idx[i] for i in indices]

        new_data = {}
        for coord, val in self._data.items():
            new_coord = tuple(coord[i] for i in indices)
            new_data[new_coord] = val
        self._data = new_data
        return self

    # Aggregations & Reductions
    def _all_values(self):
        for coord in itertools.product(*[range(len(m)) for m in self.markers]):
            yield self._data.get(coord, self.default)

    def sum(self):
        vals = [v for v in self._all_values() if v is not None]
        return sum(vals) if vals else 0

    def mean(self):
        vals = [v for v in self._all_values() if v is not None]
        return sum(vals) / len(vals) if vals else 0

    def min(self):
        vals = [v for v in self._all_values() if v is not None]
        return min(vals) if vals else None

    def max(self):
        vals = [v for v in self._all_values() if v is not None]
        return max(vals) if vals else None

    def count(self):
        return sum(1 for v in self._all_values() if v is not None)

    def where(self, predicate: Callable[[Any], bool]):
        matches = []
        for coord in itertools.product(*[range(len(m)) for m in self.markers]):
            val = self._data.get(coord, self.default)
            if predicate(val):
                marker_tuple = tuple(self.markers[dim][idx] for dim, idx in enumerate(coord))
                matches.append((marker_tuple, val))
        return matches

    # Import / Export
    def to_dict(self):
        return {
            "axes": {name: labels for name, labels in zip(self.axis_names, self.markers)},
            "default": self.default,
            "data": {str(k): v for k, v in self._data.items()}
        }

    @classmethod
    def from_dict(cls, d: dict):
        nl = cls(axes=d["axes"], default=d.get("default"))
        for k_str, val in d.get("data", {}).items():
            coord = eval(k_str)
            nl._data[coord] = val
        return nl

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dataframe(self):
        records = []
        for coord in itertools.product(*[range(len(m)) for m in self.markers]):
            rec = {
                self.axis_names[dim]: self.markers[dim][idx]
                for dim, idx in enumerate(coord)
            }
            rec["value"] = self._data.get(coord, self.default)
            records.append(rec)
        return records

    def __repr__(self):
        return f"NList(shape={self.shape}, axes={self.axis_names})"


# ==========================================
# 3. EvolveList & EvolveElement
# ==========================================

class _BatchContext:
    def __init__(self, target):
        self.target = target

    def __enter__(self):
        self.target._batch_depth += 1
        return self.target

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.target._batch_depth -= 1
        if self.target._batch_depth == 0:
            self.target.check()


class EvolveList:
    """Reactive list with transaction batching, computed elements, event hooks, and condition triggers."""

    def __init__(self, data=None):
        self.data = list(data) if data else []
        self._element_conditions = {}
        self._in_update = False
        self._batch_depth = 0
        self._on_change_callbacks = []
        self._on_append_callbacks = []
        self._on_delete_callbacks = []

    def batch(self):
        return _BatchContext(self)

    def on_change(self, callback):
        self._on_change_callbacks.append(callback)
        return callback

    def on_append(self, callback):
        self._on_append_callbacks.append(callback)
        return callback

    def on_delete(self, callback):
        self._on_delete_callbacks.append(callback)
        return callback

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [EvolveElement(self, i) for i in range(*index.indices(len(self.data)))]
        if index < 0:
            index = len(self.data) + index
        return EvolveElement(self, index)

    def __setitem__(self, index, value):
        if index < 0:
            index = len(self.data) + index
        old_val = self.data[index] if index < len(self.data) else None
        if old_val == value:
            return
        self.data[index] = value
        for cb in list(self._on_change_callbacks):
            cb(index, old_val, value)
        if self._batch_depth == 0 and not self._in_update:
            self._check_conditions_state_based()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return f"EvolveList({self.data})"

    def append(self, value):
        self.data.append(value)
        idx = len(self.data) - 1
        self._element_conditions.setdefault(idx, [])
        for cb in list(self._on_append_callbacks):
            cb(idx, value)
        if self._batch_depth == 0 and not self._in_update:
            self._check_conditions_state_based()

    def insert(self, index, value):
        self.data.insert(index, value)
        new_cond = {}
        for i, conds in self._element_conditions.items():
            new_cond[i + 1 if i >= index else i] = [(c, a, False) for c, a, _ in conds]
        self._element_conditions = new_cond
        self._element_conditions.setdefault(index, [])
        if self._batch_depth == 0 and not self._in_update:
            self._check_conditions_state_based()

    def pop(self, index=-1):
        if index < 0:
            index = len(self.data) + index
        val = self.data.pop(index)
        new_cond = {}
        for i, conds in self._element_conditions.items():
            if i == index:
                continue
            new_cond[i - 1 if i > index else i] = [(c, a, False) for c, a, _ in conds]
        self._element_conditions = new_cond
        for cb in list(self._on_delete_callbacks):
            cb(index, val)
        if self._batch_depth == 0 and not self._in_update:
            self._check_conditions_state_based()
        return val

    def clear(self):
        self.data.clear()
        self._element_conditions.clear()

    def add_condition(self, element_index, condition, action):
        if element_index not in self._element_conditions:
            self._element_conditions[element_index] = []
        self._element_conditions[element_index].append((condition, action, False))

    def check(self):
        self._check_conditions_state_based()

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


class EvolveElement:
    """Wrapper for a single reactive element inside an EvolveList."""

    def __init__(self, evolve_list: EvolveList, index: int):
        self.evolve_list = evolve_list
        self.index = index

    @property
    def value(self):
        return self.evolve_list.data[self.index]

    @value.setter
    def value(self, new_value):
        self.evolve_list[self.index] = new_value

    def set(self, value):
        self.value = value
        return self

    def when(self, condition):
        if not isinstance(condition, _Condition):
            raise TypeError("Condition must be a _Condition instance")
        return _ConditionBuilder(self.evolve_list, self.index, condition)

    def computed_from(self, sources: List['EvolveElement'], fn: Callable[..., Any]):
        source_indices = [s.index for s in sources]
        def update_val(*args, **kwargs):
            vals = [s.value for s in sources]
            self.value = fn(*vals)

        self.evolve_list.on_change(lambda idx, old, new: update_val() if idx in source_indices else None)
        update_val()
        return self

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
        return f"EvolveElement({self.value} @ index {self.index})"


class _ConditionBuilder:
    def __init__(self, evolve_list, element_index, condition):
        self.evolve_list = evolve_list
        self.element_index = element_index
        self.condition = condition

    def do(self, action, *args, **kwargs):
        wrapped = (lambda: action(*args, **kwargs)) if (args or kwargs) else action
        self.evolve_list.add_condition(self.element_index, self.condition, wrapped)
        return self.evolve_list[self.element_index]

    def print(self, message):
        return self.do(lambda: print(message))

    def set_value(self, target_index, value):
        return self.do(lambda: self.evolve_list.__setitem__(target_index, value))


class _Condition:
    def __init__(self, evolve_list, func):
        self.evolve_list = evolve_list
        self.func = func

    def check(self):
        try:
            return bool(self.func())
        except Exception:
            return False

    def __and__(self, other):
        return _Condition(self.evolve_list, lambda: self.check() and other.check())

    def __or__(self, other):
        return _Condition(self.evolve_list, lambda: self.check() or other.check())

    def __invert__(self):
        return _Condition(self.evolve_list, lambda: not self.check())


# ==========================================
# 4. FlexDict & EvolveDict
# ==========================================

class FlexDict(dict):
    """
    A smart dictionary supporting dot-access, auto-vivification, key flattening,
    unflattening, and deep recursive merging.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        for k, v in dict(*args, **kwargs).items():
            self[k] = self._wrap(v)

    def _wrap(self, value):
        if isinstance(value, dict) and not isinstance(value, FlexDict):
            return FlexDict(value)
        return value

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        if name not in self:
            self[name] = FlexDict()
        return self[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self[name] = self._wrap(value)

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            super().__delattr__(name)

    def flatten(self, sep=".") -> Dict[str, Any]:
        result = {}
        def _flatten(current, prefix=""):
            for k, v in current.items():
                new_key = f"{prefix}{sep}{k}" if prefix else str(k)
                if isinstance(v, dict):
                    _flatten(v, new_key)
                else:
                    result[new_key] = v
        _flatten(self)
        return result

    @classmethod
    def unflatten(cls, flat_dict: Dict[str, Any], sep="."):
        result = cls()
        for key, value in flat_dict.items():
            parts = key.split(sep)
            curr = result
            for part in parts[:-1]:
                if part not in curr or not isinstance(curr[part], dict):
                    curr[part] = cls()
                curr = curr[part]
            curr[parts[-1]] = value
        return result

    def merge(self, other: dict):
        for k, v in other.items():
            if k in self and isinstance(self[k], dict) and isinstance(v, dict):
                if isinstance(self[k], FlexDict):
                    self[k].merge(v)
                else:
                    self[k] = FlexDict(self[k])
                    self[k].merge(v)
            else:
                self[k] = self._wrap(v)
        return self

    def to_dict(self) -> dict:
        res = {}
        for k, v in self.items():
            if isinstance(v, FlexDict):
                res[k] = v.to_dict()
            else:
                res[k] = v
        return res


class EvolveDict:
    """Reactive dictionary with key-level condition triggers, batching, and event watchers."""

    def __init__(self, initial: dict = None):
        self._data = FlexDict(initial or {})
        self._conditions = []
        self._batch_depth = 0
        self._on_change_callbacks = []

    def batch(self):
        return _BatchContext(self)

    def on_change(self, callback):
        self._on_change_callbacks.append(callback)
        return callback

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        old_val = self._data.get(key)
        self._data[key] = value
        for cb in list(self._on_change_callbacks):
            cb(key, old_val, value)
        if self._batch_depth == 0:
            self.check()

    def __delitem__(self, key):
        if key in self._data:
            old_val = self._data[key]
            del self._data[key]
            for cb in list(self._on_change_callbacks):
                cb(key, old_val, None)
            if self._batch_depth == 0:
                self.check()

    def when(self, key_condition):
        return _DictConditionBuilder(self, key_condition)

    def check(self):
        new_conds = []
        for key, cond_fn, action, last_state in self._conditions:
            try:
                curr_state = bool(cond_fn())
                if curr_state and not last_state:
                    if callable(action):
                        action()
                    else:
                        print(action)
                new_conds.append((key, cond_fn, action, curr_state))
            except Exception:
                new_conds.append((key, cond_fn, action, False))
        self._conditions = new_conds

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __repr__(self):
        return f"EvolveDict({dict(self._data)})"


class _DictConditionBuilder:
    def __init__(self, evolve_dict, condition_fn):
        self.evolve_dict = evolve_dict
        self.condition_fn = condition_fn

    def do(self, action):
        fn = self.condition_fn if callable(self.condition_fn) else (lambda: self.condition_fn)
        self.evolve_dict._conditions.append((None, fn, action, False))
        self.evolve_dict.check()
        return self.evolve_dict


# ==========================================
# 5. FlexTree
# ==========================================

class FlexTree:
    """Hierarchical tree container supporting path querying, node search, and tree traversal."""

    def __init__(self, name: str, value: Any = None, parent: Optional['FlexTree'] = None):
        self.name = name
        self.value = value
        self.parent = parent
        self.children: Dict[str, 'FlexTree'] = {}

    def add_child(self, name: str, value: Any = None) -> 'FlexTree':
        child = FlexTree(name, value, parent=self)
        self.children[name] = child
        return child

    def remove_child(self, name: str) -> Optional['FlexTree']:
        return self.children.pop(name, None)

    @property
    def path(self) -> str:
        if self.parent is None:
            return f"/{self.name}"
        return f"{self.parent.path}/{self.name}".replace("//", "/")

    def find(self, path: str) -> Optional['FlexTree']:
        parts = [p for p in path.strip('/').split('/') if p]
        if not parts:
            return self

        curr = self
        if parts[0] == curr.name:
            parts = parts[1:]

        for part in parts:
            if part in curr.children:
                curr = curr.children[part]
            else:
                return None
        return curr

    def traverse(self, method: str = "dfs") -> Iterator['FlexTree']:
        if method.lower() == "dfs":
            yield self
            for child in self.children.values():
                yield from child.traverse(method="dfs")
        elif method.lower() == "bfs":
            queue = [self]
            while queue:
                curr = queue.pop(0)
                yield curr
                queue.extend(curr.children.values())
        else:
            raise ValueError("Method must be 'dfs' or 'bfs'")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "children": [child.to_dict() for child in self.children.values()]
        }

    @classmethod
    def from_dict(cls, d: dict, parent=None) -> 'FlexTree':
        node = cls(d["name"], d.get("value"), parent=parent)
        for child_d in d.get("children", []):
            node.children[child_d["name"]] = cls.from_dict(child_d, parent=node)
        return node

    def __repr__(self):
        return f"FlexTree({self.name!r}, value={self.value!r}, children={len(self.children)})"