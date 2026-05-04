"""
datatypeplus: A small library providing advanced data structures.

Classes:
- FlexString: Mutable string with list-like and string-like methods.
- NList: Multi-dimensional container with labeled axes.
- EvolveList & EvolveElement: Reactive list with condition-based triggers.

Usage:
    from datatypeplus import FlexString, NList, EvolveList, EvolveElement, info
"""

from .flow import FlexString, NList, EvolveList, EvolveElement, info

# Public API
__all__ = [
    "FlexString",
    "NList",
    "EvolveList",
    "EvolveElement",
    "info",
]
