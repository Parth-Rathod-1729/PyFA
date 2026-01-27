from __future__ import annotations
from typing import Any
from PyFA_Exception import StateError, TransitionSymbolError, MiscError
from utils import TransitionSymbol

#TODO: Implement NFA (without NULL transition)
#TODO: Implement NFA (with NULL transition)

class State:
    def __init__(self, name: str, isFinal: bool = False, isInitial: bool = False,
                 outTransitions: dict[TransitionSymbol, State] | dict[Any, State] = None):
        self.name = name
        self.outTransitions = outTransitions
        self.isFinal = isFinal
        self.isInitial = isInitial

    def validate(self, inputSymbols: list[TransitionSymbol] | list[Any] = None) -> bool:
        if self.outTransitions is None:
            raise StateError(f"Outgoing transitions for the state '{self.name}' are not defined. use State.setTransitions( < outgoingTransitions > ) for setting the outgoing transitions. ")

        tempInpSymList = list(self.outTransitions.keys())

        for i in range(len(tempInpSymList)):
            if not isinstance(tempInpSymList[i], TransitionSymbol):
                tempInpSymList[i] = TransitionSymbol(tempInpSymList[i])

        if inputSymbols is not None:
            for i in range(len(inputSymbols)):
                if not isinstance(inputSymbols[i], TransitionSymbol):
                    inputSymbols[i] = TransitionSymbol(inputSymbols[i])

            if any(map(lambda sym: sym == TransitionSymbol("Epsilon"), [*inputSymbols, *tempInpSymList])):
                raise TransitionSymbolError(
                    errorMsg = "Epsilon / NULL transition symbol is not allowed as a state's transition symbol",
                    expected = inputSymbols,
                    received = tempInpSymList
                )
            set_tempInpSymList = set(tempInpSymList)
            set_inputSymbols = set(inputSymbols)
            if set_inputSymbols != set_tempInpSymList:
                raise TransitionSymbolError(
                    errorMsg=f"The state '{self.name}' has different set of transition symbols than provided",
                    expected=inputSymbols,
                    received=tempInpSymList
                )

        for inpSym, state_ in self.outTransitions.items():
            if not isinstance(state_, State):
                raise StateError(f"{self.name} -- {inpSym} --> [] is not a State.")
        return True  # this state is a valid DFA state

    def setTransitions(self, outTransitions: dict[TransitionSymbol, State] | dict[str, State]) -> None:
        TransitionSymbol_state_mapping = dict()
        for key, value in outTransitions.items():
            if not isinstance(key, TransitionSymbol):
                TransitionSymbol_state_mapping[TransitionSymbol(key)] = value
            else:
                TransitionSymbol_state_mapping[key] = value
        self.outTransitions = TransitionSymbol_state_mapping

    def debugPrintState(self):
        print(f"< name: {self.name}, \noutTransitions: {self.outTransitions}\nisFinal: {self.isFinal}, isInitial: {self.isInitial} >")

    def goto(self, inputSymbol: TransitionSymbol) -> State:
        try:
            return self.outTransitions[inputSymbol]
        except KeyError:
            self.debugPrintState()
            raise TransitionSymbolError(f"Input symbol '{inputSymbol}' was not found for state '{self.name}'")
        except TypeError:
            self.debugPrintState()
            raise StateError(f"outgoing transitions for the state '{self.name}' are not defined. use State.setTransitions(< outgoingTransitions >) to set the outgoing transitions for this state.")
        except Exception as err:
            raise MiscError(err)


class DFA:
    def __init__(self, states: list[State] = None, initialState: State = None):
        self.inputSymbols = None
        self.finals = None
        self.states = states
        self.initialState = initialState
        self.stateNtransitions = None
        if states:
            self.validate()

    def __str__(self):
        self.validate()
        ret = "State | "
        for inpSym in self.inputSymbols:
            ret += f"{inpSym} | "
        dashLength = len(ret)
        ret += "\n"
        ret += "-" * dashLength
        ret += "\n"
        ret = f'{"-" * dashLength}\n' + ret

        for state_ in sorted(self.states, key=lambda state_: state_.name):
            prefix = "  "
            suffix = "   "
            if state_.isInitial and not state_.isFinal:
                prefix = "-> "
                suffix = "  "
            if state_.isFinal and not state_.isInitial:
                suffix = "*  "
            if state_.isFinal and state_.isInitial:
                prefix = "-> "
                suffix = "* "

            ret += f"{prefix}{state_.name}{suffix}| "
            for inpSym in self.inputSymbols:
                ret += f"{state_.outTransitions[inpSym].name} | "
            ret += "\n"

        ret += "-" * dashLength
        ret += "\n"

        return ret

    def validate(self) -> bool:
        if self.initialState is None:
            raise StateError("Initial State was not found.")
        if self.finals is None:
            self.finals = []
        if self.states is None:
            raise StateError("This DFA has no states")
        else:
            if self.initialState not in self.states:
                raise StateError(
                    errorMsg = "Initial state is absent from the given set of states.",
                    expected = self.initialState.name,
                    received = f"A state not in {[_state.name for _state in self.states]}"
                )
            if self.inputSymbols is None:
                self.states[0].validate()
                self.inputSymbols = list(self.states[0].outTransitions.keys())
            for state_ in self.states:
                state_.validate(self.inputSymbols)
        if self.stateNtransitions is None:
            self.stateNtransitions = dict()
            for state_ in self.states:
                self.stateNtransitions[state_.name] = state_.outTransitions

        return True  # this DFA is valid

    def define(self, stateNtransitions: dict[str, dict[str, str]] | dict[str, dict[TransitionSymbol, str]] | dict[str, dict[Any, str]], initial: str, finals: list[str]) -> None:
        name_state_mapping: dict[str, State] = {}
        for name in stateNtransitions.keys():
            isNAMEfinal = False
            isNAMEinitial = False
            if name == initial:
                isNAMEinitial = True
            if name in finals:
                isNAMEfinal = True
            name_state_mapping[name] = State(name, isInitial=isNAMEinitial, isFinal=isNAMEfinal)
        for name, transitions in stateNtransitions.items():
            try:
                outTransition = {TransitionSymbol(inpSymbol): name_state_mapping[stateName] for inpSymbol, stateName in transitions.items()}
                name_state_mapping[name].setTransitions(outTransition)
                if name_state_mapping[name].isInitial:
                    self.initialState = name_state_mapping[name]
            except KeyError as keyErr:
                raise StateError(
                    errorMsg = f"State with name {keyErr} was not found"
                )
            except Exception as err:
                raise MiscError(err)

        self.states = list(name_state_mapping.values())
        self.inputSymbols = list(stateNtransitions[list(stateNtransitions.keys())[0]].keys())
        self.finals = [state_ for state_ in self.states if state_.isFinal]
        self.stateNtransitions = stateNtransitions

    def check(self, inputTransitionSymbolSequence: list[TransitionSymbol] | list[Any] | str) -> bool:
        if len(inputTransitionSymbolSequence) == 0 or any(map(lambda sym: sym == TransitionSymbol("Epsilon"), inputTransitionSymbolSequence)):
            raise TransitionSymbolError("Epsilon transition not in DFA")
        firstTransitionSymbol = inputTransitionSymbolSequence[0]
        if isinstance(firstTransitionSymbol, TransitionSymbol):
            curState = self.initialState.goto(firstTransitionSymbol)
        else:
            curState = self.initialState.goto(TransitionSymbol(firstTransitionSymbol))
        for transitionSymbol in inputTransitionSymbolSequence[1:]:
            if isinstance(transitionSymbol, TransitionSymbol):
                curState = curState.goto(transitionSymbol)
            else:
                curState = curState.goto(TransitionSymbol(transitionSymbol))
            if curState is None:
                break
        if curState.isFinal:
            print(f"< {inputTransitionSymbolSequence} >: Accepted")
            return True
        else:
            print(f"< {inputTransitionSymbolSequence} >: Rejected")
            return False

    def removeUnreachable(self) -> None:
        visited = {self.initialState}
        BFSqueue = [self.initialState]
        while len(BFSqueue) > 0:
            curState = BFSqueue.pop(0)
            for neighbourState in curState.outTransitions.values():
                if neighbourState not in visited:
                    BFSqueue.append(neighbourState)
                    visited |= {neighbourState}
        self.states = sorted(list(visited), key=lambda state_: state_.isInitial, reverse=True)

    def getStateWithName(self, name_: str) -> State | None:
        for state_ in self.states:
            if state_.name == name_:
                return state_
        return None

    @staticmethod
    def _findSetIdxOf(state_: State, partition: list[list[State]]) -> int | None:

        for i in range(len(partition)):
            if state_ in partition[i]:
                return i
        return None

    def _make_TSTT(self, state_: State, partition: list[list[State]]) -> tuple[tuple[TransitionSymbol, int]] | tuple[None]:
        setTransitionTuples = []
        for inpSym in self.inputSymbols:
            setIdx = self._findSetIdxOf(state_.goto(inpSym), partition)
            if setIdx is None:
                return (None,)
            setTransitionTuples.append((inpSym, setIdx))
        return tuple(setTransitionTuples)

    def _refinePartition(self, partition: list[list[State]]) -> list[list[State]]:
        refinedPartition = []
        for SL in partition:
            CSSLeaderTSTT_CSS = {
                self._make_TSTT(SL[0], partition): [SL[0]]
            }
            for state_ in SL[1:]:
                state_TSTT = self._make_TSTT(state_, partition)
                if state_TSTT in CSSLeaderTSTT_CSS:
                    CSSLeaderTSTT_CSS[state_TSTT].append(state_)
                else:
                    CSSLeaderTSTT_CSS[state_TSTT] = [state_]
            refinedPartition.extend(list(CSSLeaderTSTT_CSS.values()))

        return refinedPartition

    @staticmethod
    def _printablePartition(partition: list[list[State]]) -> list[list[str]]:
        ret = []
        for SL in partition:
            retSL = [state_.name for state_ in SL]
            ret.append(retSL)
        return ret

    def minimise(self) -> None:
        self.removeUnreachable()
        print(self)
        PI_0 = [[], []]

        for state_ in self.states:
            PI_0[state_.isFinal].append(state_)
        if len(PI_0[0]) == 0:
            PI_0.pop(0)
        prevPartition = PI_0
        curPartition = self._refinePartition(PI_0)
        i = 0
        print(f"PI_{i}: ", self._printablePartition(prevPartition))
        i += 1
        print(f"PI_{i}: ", self._printablePartition(curPartition))
        while prevPartition != curPartition:
            prevPartition = curPartition
            curPartition = self._refinePartition(curPartition)
            i += 1
            print(f"PI_{i}: ", self._printablePartition(curPartition))

        print()
        mDFA_SNT = {}
        mDFA_names = []
        mDFA_listOfTSTT = []
        for SL in curPartition:
            mDFA_names.append("".join([state_.name for state_ in SL]))
            mDFA_listOfTSTT.append(self._make_TSTT(SL[0], curPartition))

        for stateName, state_TSTT in zip(mDFA_names, mDFA_listOfTSTT):
            SNT_valueDict = dict()
            for setTransitionTuple in state_TSTT:
                SNT_valueDict[setTransitionTuple[0]] = mDFA_names[setTransitionTuple[1]]
            mDFA_SNT[stateName] = SNT_valueDict

        mDFA_initial = mDFA_names[self._findSetIdxOf(self.initialState, curPartition)]
        mDFA_finals = list({mDFA_names[self._findSetIdxOf(finalState_, curPartition)] for finalState_ in self.finals})
        self.define(mDFA_SNT, mDFA_initial, mDFA_finals)
