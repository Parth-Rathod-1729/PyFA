from __future__ import annotations
from typing import Any

class TransitionSymbol:
    def __init__(self, symbolValue):
        self.symbolValue = symbolValue

    def __repr__(self):
        return f"TransitionSymbol< {self.symbolValue.__str__()} >"

    def __str__(self):
        return self.symbolValue.__repr__()
      
    @staticmethod
    def _flattenDict(flatable: dict[Any, Any]) -> tuple[tuple[Any]]:
        flattened = list()
        for key, value in sorted(flatable.items(), key=lambda kvPair: str(kvPair[0])):
            if isinstance(value, dict):
                flattened.append((key, TransitionSymbol._flattenDict(value)))
            else:
                flattened.append((key, value))
        return tuple(flattened)

    def __hash__(self) -> int:
        try:
            return self.symbolValue.__hash__()
        except:
            if isinstance(self.symbolValue, (list, set)):
                return hash(tuple(self.symbolValue))
            if isinstance(self.symbolValue, dict):
                return hash(TransitionSymbol._flattenDict(self.symbolValue))
            if type(self.symbolValue).__module__ != "builtins":
                return hash(TransitionSymbol._flattenDict(self.symbolValue.__dict__))
            print(f"TransitionSymbolWarning: The TransitionSymbol({self.symbolValue}) could not be hashed. Unexpected Errors may occur")
            return id(self)

    def __eq__(self, other: TransitionSymbol | Any) -> bool:
        if isinstance(other, TransitionSymbol):
            return self.symbolValue == other.symbolValue
        else:
            return self.symbolValue == other
