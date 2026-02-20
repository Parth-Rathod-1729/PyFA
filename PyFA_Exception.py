from __future__ import annotations
from typing import Any

class BasePyFAException(BaseException):
    def __init__(self, errorType: str, coreErrorMessage: str, expected: Any = None, received: Any = None, *args):

        self.coreErrorMessage = coreErrorMessage
        self.errorType = errorType
        self.expected = expected or None
        self.received = received or None
        self.messageToBaseException = self.coreErrorMessage
        if self.expected:
            self.messageToBaseException += f"\n\tExpected: {self.expected}"

        if self.received:
            self.messageToBaseException += f"\n\tReceived: {self.received}"

        super().__init__(self.messageToBaseException, *args)

    def __str__(self):
        return self.messageToBaseException


class BasePyFAWarning:
    pass

class StateError(BasePyFAException):
    def __init__(self, errorMsg: str, expected: State = None, received: Any = None):
        super().__init__(errorType = "StateError", coreErrorMessage = errorMsg, expected = expected, received = received)

class TransitionSymbolError(BasePyFAException):
    def __init__(self,  errorMsg: str, expected: TransitionSymbol | Any = None, received: TransitionSymbol | Any = None):
        super().__init__(errorType = "TransitionSymbolError", coreErrorMessage = errorMsg, expected = expected, received = received)

class MiscError(BasePyFAException):
    def __init__(self,  errorMsg: str | Any, expected: Any = None, received: Any = None):
        super().__init__(errorType = "MiscError", coreErrorMessage = errorMsg, expected = expected, received = received)


