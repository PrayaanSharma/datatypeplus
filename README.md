# datatypeplus

Datatypeplus is a Python library that provides advanced data structures and reactive containers.

---

## Import

from datatypeplus import FlexString, NList, EvolveList, EvolveElement, info

---

## FlexString

A mutable, list-like string class with full edit and transformation support.

### Example

fs = FlexString("Hello")
fs.append(" World")
fs[0] = "h"
fs.replace("World", "Python")
fs.upper()
fs[0:3] = "Hey"
fs.extend("!!")
fs.insert(0, ">")
print(fs)  # >>> HEYLO PYTHON!!

### Methods

append(value)  
 Add text to the end of the string.

extend(value)  
 Extend with multiple characters or another string.

insert(index, value)  
 Insert text at a specific position.

replace(old, new)  
 Replace all occurrences of a substring.

upper()  
 Convert all characters to uppercase (in place).

lower()  
 Convert all characters to lowercase (in place).

__getitem__(index) / __setitem__(index, value)  
 Access or modify by index or slice.

---

## NList

A labeled, multi-dimensional datatypeplus for structured data access.  
Each axis has a name and markers, which can be used to locate data points.

### Example

nl = NList(
    axes={
        "Year": [2011, 2012, 2013],
        "Month": ["Jan", "Feb"],
        "City": ["NY", "LA"]
    },
    default=0
)

nl.set(2011, "Jan", "NY", value=100)
nl.set(2012, "Feb", "LA", value=200)

print(nl.get(2011, "Jan", "NY"))  # 100
print(nl.get(2012, "Feb", "LA"))  # 200
print(nl.get(2013, "Jan", "NY"))  # 0 (default)

### Methods

set(*markers, value)  
 Set a value at the specified axis markers.

get(*markers)  
 Retrieve a value using axis markers.

axes  
 Dictionary of all defined axes.

shape  
 List of axis lengths.

__repr__()  
 Returns a string summary of the structure.

---

## EvolveList and EvolveElement

Reactive lists that automatically trigger actions when certain conditions become true.

### Example

el = EvolveList([10, 20, 30])

el[0].when(el[0] == 10).print("Element 0 hit 10!")
el[2].when(el[2] == 15).do(lambda: print("Element 2 hit 15!"))

el[0].value = 10
el[2] = 15
el.append(40)

# Multi-condition using & (and), | (or), and ~ (not)
el[1].when((el[1] == 20) & (el[2] != 30)).do(lambda: el.__setitem__(1, 99))
el[2].when((el[2] > 10) | (el[0] == 10)).print("Element 2 triggered by OR condition")
el[0].when(~(el[0] == 5)).print("Element 0 is NOT 5")

print(el)

### Methods

append(value)  
 Add an element to the list.

__setitem__(index, value)  
 Set a value at a position; triggers conditions if met.

__getitem__(index)  
 Return an EvolveElement wrapper for the element.

el[i].value  
 Access or modify an element’s stored value.

el[i].when(condition)  
 Define a reactive condition for an element.

el[i].when(...).do(action)  
 Run a custom function when the condition becomes true.

el[i].when(...).print(message)  
 Print a message when the condition becomes true.

check()  
 Manually re-evaluate all conditions.

|=or
&=and
~=not
---

## info()

Prints metadata about the library.

### Example

print(info())

Output:

Datatypeplus v1.1.1  
Includes: FlexString, NList, EvolveList, EvolveElement  
License: MIT

---

## File Structure

datatypeplus/  
│  
├── __init__.py  
├── flow.py  
├── setup.py  
├── test.py  
├── README.md  
└── LICENSE.txt

---

## Installation

Local install for development:

pip install -e .

After install:

from datatypeplus import *

## Upgrade

To upgrade:

pip install datatypeplus --upgrade
