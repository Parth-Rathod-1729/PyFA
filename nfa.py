from __future__ import annotations
from typing import Any
from utils import TransitionSymbol
from PyFA_Exception import TransitionSymbolError, StateError, MiscError

class NFAstate:
    def __init__(self, name: str, isFinal: bool = False, isInitial: bool = False,
                 outTransitions: dict[TransitionSymbol, tuple[NFAstate]] | dict[Any, tuple[NFAstate]
                 | dict[TransitionSymbol, list[str]] | dict[Any, list[str]]] = None):
        self.name = name
        self.outTransitions = outTransitions
        self.isFinal = isFinal
        self.isInitial = isInitial

    @staticmethod
    def getNamesOfStates(tupleOfNFAstates: tuple[NFAstate]) -> list[str]:
        ret = []
        for state_ in tupleOfNFAstates:
            ret.append(state_.name)
        return ret

    def setTransitions(self, outTransitions: dict[TransitionSymbol, tuple[NFAstate]] | dict[Any, tuple[NFAstate]]) -> None:
        newOutTransitions = dict()
        for transitionSymbol, tupleOfNFAstates in outTransitions.items():
            if not isinstance(transitionSymbol, TransitionSymbol):
                newOutTransitions[TransitionSymbol(transitionSymbol)] = tupleOfNFAstates
            else:
                newOutTransitions[transitionSymbol] = tupleOfNFAstates

        self.outTransitions = newOutTransitions

    def goto(self, inputSymbol: TransitionSymbol) -> tuple[NFAstate]:
        try:
            return self.outTransitions[inputSymbol]
        except KeyError:
            return tuple()
        except TypeError:
            return tuple()
        except Exception as err:
            raise MiscError(err)

    def getEpsilonClosure(self) -> tuple[NFAstate]:
        ret = set()
        ret.add(self)
        nextRecurCallTargetStates = []
        try:
            for recurTargetState in self.goto(TransitionSymbol.Epsilon()):
                nextRecurCallTargetStates.append(recurTargetState)
                ret.add(recurTargetState)
        finally:
            if len(nextRecurCallTargetStates) == 0:
                return tuple(ret)
            for recurTargetState in nextRecurCallTargetStates:
                recurTargetState_epsilonClosure = recurTargetState.getEpsilonClosure()
                for recurTargetState_epsilonClosure_destState in recurTargetState_epsilonClosure:
                    ret.add(recurTargetState_epsilonClosure_destState)
            return tuple(ret)


class NFA:
    def __init__(self, states: list[NFAstate] = None, initialState: NFAstate = None):
        self.inputSymbols = None
        self.finals = None
        self.states = states
        self.initialState = initialState
        self.stateNtransitions = None
        self.inputSymbols: set[TransitionSymbol] = None

    def define(self, stateNtransitions: dict[str, dict[str, list[str]]] | dict[str, dict[TransitionSymbol, list[str]]] | dict[str, dict[Any, list[str]]], initial: str, finals: list[str]) -> None:
        name_state_mapping: dict[str, NFAstate] = {}
        setOfInputSymbols: set[TransitionSymbol] = set()
        for name in stateNtransitions.keys():
            isNAMEfinal = False
            isNAMEinitial = False
            if name == initial:
                isNAMEinitial = True
            if name in finals:
                isNAMEfinal = True
            name_state_mapping[name] = NFAstate(name, isInitial=isNAMEinitial, isFinal=isNAMEfinal)
        for stateName, transitionDict in stateNtransitions.items():
            outTransitions: dict[TransitionSymbol, tuple[NFAstate]] = dict()
            for transSym, destNFAstateNameList in transitionDict.items():
                for destNFAstateName in destNFAstateNameList:
                    try:
                        destNFAstateInstance = name_state_mapping[destNFAstateName]
                    except KeyError as keyErr:
                        newStateName = str(keyErr)[1:-1]
                        destNFAstateInstance = NFAstate(newStateName, isInitial=(True if newStateName == initial else False), isFinal=(True if newStateName in finals else False))
                    finally:
                        name_state_mapping[destNFAstateName] = destNFAstateInstance

                if not isinstance(transSym, TransitionSymbol):
                    transSym = TransitionSymbol(transSym)
                setOfInputSymbols.add(transSym)
                destNFAstateInstanceTuple = tuple(
                    [name_state_mapping[name] for name in destNFAstateNameList]
                )
                outTransitions[transSym] = destNFAstateInstanceTuple
            name_state_mapping[stateName].setTransitions(outTransitions=outTransitions)
            if name_state_mapping[stateName].isInitial:
                self.initialState = name_state_mapping[stateName]

        self.states = list(name_state_mapping.values())
        self.inputSymbols = setOfInputSymbols
        self.finals = [name_state_mapping[stateName] for stateName in finals]
        self.stateNtransitions = stateNtransitions

    def getStateWithName(self, name_: str) -> NFAstate | None:
        for state_ in self.states:
            if state_.name == name_:
                return state_
        return None

    @staticmethod
    def _isFinalPresentInThis(tupleOfNFAstates: tuple[NFAstate]) -> bool:
        for state_ in tupleOfNFAstates:
            if state_.isFinal:
                return True
        return False

    def check(self, inputTransitionSymbolSequence: list[TransitionSymbol] | list[Any] | str) -> bool:
        if len(inputTransitionSymbolSequence) == 0:
            return NFA._isFinalPresentInThis(self.initialState.getEpsilonClosure())

        curReachedStates = set()
        curReachedStates.add(self.initialState)
        for curTransSym in inputTransitionSymbolSequence:
            immediateNextStates = set()
            for state_ in curReachedStates:
                immediatelyReachableByCurTransSym = None
                try:
                    immediatelyReachableByCurTransSym = set(state_.goto(curTransSym))
                finally:
                    if immediatelyReachableByCurTransSym is not None:
                        immediateNextStates.update(immediatelyReachableByCurTransSym)

            for state_ in curReachedStates:
                for state__ in state_.getEpsilonClosure():
                    reachableViaEpsilonClosure = None
                    try:
                        reachableViaEpsilonClosure = set(state__.goto(curTransSym))
                    finally:
                        if reachableViaEpsilonClosure is not None:
                            immediateNextStates.update(reachableViaEpsilonClosure)

            curReachedStates = immediateNextStates.copy()

        return NFA._isFinalPresentInThis(tuple(curReachedStates))
