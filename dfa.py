
# StateError
# InputSymbolError
# TransitionError
# MiscError

#TODO: remove the '_' not being able to be used as a transition symbol, Handle the minimisation without the use of '_' (use list of tuples/list perhaps)
#TODO: Add the TransitionSymbol or TerminalSymbol class that is able to use any string/Integer/Float/(Potentially any Python Object) as a transition symbol (Goal: Markov Chains)
#TODO: Add the Error handling with above 4 errors to start with

class State:
    def __init__(self, name, isFinal = False, isInitial = False, outTransitions = None):
        self.name = name
        self.outTransitions = outTransitions
        self.isFinal = isFinal
        self.isInitial = isInitial

    def validate(self, inputSymbols = None):
        if self.outTransitions is None:
            raise Exception(f"StateError: Outgoing transitions for the state '{self.name}' are not defined. use State.setTransitions( < outgoingTransitions > ) for setting the outgoing transitions. ")

        tempInpSymList = list(self.outTransitions.keys())
        if all(list(map(lambda inpSym: len(inpSym) == 1,tempInpSymList))):  # checks if all inputSymbol are of single length or not
            if not all(list(map(lambda inpSym: inpSym != "_",tempInpSymList))):  # this DFA implementation will not allow "_" to be a valid inputSymbol as we are using it in the minimisation algorithm (this will change in the future)
                raise Exception(f"InputSymbolError: '_' are not allowed to be a valid input symbol in this DFA implementation. (State => '{self.name}') ")
        else:
            raise Exception("InputSymbolError: length of input symbol must be exactly 1. ")

        if inputSymbols is not None:
            if set(inputSymbols) != set(tempInpSymList):
                raise Exception(f"InputSymbolError: the state '{self.name}' has different set of input symbols than provided\n\tProvided: {inputSymbols}\n\tOutgoing: {tempInpSymList}")

        for inpSym, state_ in self.outTransitions.items():
            if not isinstance(state_, State):
                raise Exception(f"StateError: {self.name} -- {inpSym} --> [] is not a State. ")
        return True # this state is a valid DFA state

    def setTransitions(self, outTransitions):
        self.outTransitions = outTransitions

    def debugPrintState(self):
        print(f"< name: {self.name}, \noutTransitions: {self.outTransitions}\nisFinal: {self.isFinal}, isInitial: {self.isInitial} >")

    def goto(self, inputSymbol):
        try:
            return self.outTransitions[inputSymbol]
        except KeyError:
            self.debugPrintState()
            raise Exception(f"InputSymbolError: input symbol '{inputSymbol}' was not found for state '{self.name}'")
        except TypeError:
            self.debugPrintState()
            raise Exception(f"StateError: outgoing transitions for the state '{self.name}' are not defined. use State.setTransitions(< outgoingTransitions >) to set the outgoing transitions for this state. ")
        except Exception as err:
            raise Exception(f"MiscError: {err}")


class DFA:
    def __init__(self, states = None, initial = None):
        self.inputSymbols = None
        self.finals = None
        self.states = states
        self.initialState = initial
        self.stateNtransitions = None
        if states:
            self.validate()

    def __str__(self):
        ret = "State | "
        for inpSym in self.inputSymbols:
            ret += f"{inpSym} | "
        dashLength = len(ret)
        ret += "\n"
        ret += "-"*dashLength
        ret += "\n"
        ret = f'{"-" * dashLength}\n' + ret

        for state_ in sorted(self.states, key = lambda state_: state_.name):
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

        ret += "-"*dashLength
        ret += "\n"

        return ret

    def validate(self):
        if self.initialState is None:
            raise Exception("StateError: Initial state not found. ")
        if self.finals is None:
            self.finals = []
        if self.states is None:
            raise Exception("StateError: This DFA has no states. ")
        else:
            if self.inputSymbols is None:
                self.states[0].validate()
                self.inputSymbols = list(self.states[0].outTransitions.keys())
            for state_ in self.states:
                state_.validate(self.inputSymbols)
        if self.stateNtransitions is None:
            self.stateNtransitions = dict()
            for state_ in self.states:
                self.stateNtransitions[state_.name] = state_.outTransitions

        return True # this DFA is valid

    def define(self, stateNtransitions, initial, finals):
        name_state_mapping = {}
        for name in stateNtransitions.keys():
            isNAMEfinal = False
            isNAMEinitial = False
            if name == initial:
                isNAMEinitial = True
            if name in finals:
                isNAMEfinal = True
            name_state_mapping[name] = State(name, isInitial=isNAMEinitial, isFinal=isNAMEfinal)
        for name, transitions in stateNtransitions.items():
            outTransition = {inpSymbol: name_state_mapping[stateName] for inpSymbol, stateName in transitions.items()}
            name_state_mapping[name].setTransitions(outTransition)
            if name_state_mapping[name].isInitial :
                self.initialState = name_state_mapping[name]

        self.states = list(name_state_mapping.values())
        self.inputSymbols = list(stateNtransitions[list(stateNtransitions.keys())[0]].keys())
        self.finals = [state_ for state_ in self.states if state_.isFinal]
        self.stateNtransitions = stateNtransitions

    def check(self, inputStr):
        if len(inputStr) == 0:
            raise Exception("InputSymbolError: Epsilon transition not in DFA")
        curState = self.initialState.goto(inputStr[0])
        for inpSymbol in inputStr[1:]:
            curState = curState.goto(inpSymbol)
            if curState is None:
                break
        if curState.isFinal:
            print(f"'{inputStr}': Accepted")
            return True
        else:
            print(f"'{inputStr}': Rejected")
            return False
          
    def removeUnreachable(self):
        visited = {self.initialState}
        BFSqueue = [self.initialState]
        while len(BFSqueue) > 0:
            curState = BFSqueue.pop(0)
            for neighbourState in curState.outTransitions.values():
                if neighbourState not in visited:
                    BFSqueue.append(neighbourState)
                    visited |= {neighbourState}
        self.states = sorted(list(visited), key = lambda state_: state_.isInitial, reverse=True)

    def _getStateWithName(self, name_):
        for state_ in self.states:
            if state_.name == name_:
                return state_
        return None

    @staticmethod
    def _findSetIdxOf(state_, partition):
        for i in range(len(partition)):
            if state_ in partition[i]:
                return i
        return None

    def _make_STS(self, state_, partition):
        setTransitionSubstrings = []
        for inpSym in self.inputSymbols:
            setIdx = self._findSetIdxOf(state_.goto(inpSym), partition)
            if setIdx is None:
                return None
            setTransitionSubstrings.append(f"{inpSym}_{setIdx}")
        return "__".join(setTransitionSubstrings)

    def _refinePartition(self, partition):
        refinedPartition = []
        for SL in partition:
            CSSLeaderSTS_CSS = {
                self._make_STS(SL[0], partition): [SL[0]]
            }
            for state_ in SL[1:]:
                state_STS = self._make_STS(state_, partition)
                if state_STS in CSSLeaderSTS_CSS:
                    CSSLeaderSTS_CSS[state_STS].append(state_)
                else:
                    CSSLeaderSTS_CSS[state_STS] = [state_]
            refinedPartition.extend(list(CSSLeaderSTS_CSS.values()))

        return refinedPartition

    @staticmethod
    def _printablePartition(partition):
        ret = []
        for SL in partition:
            retSL = [state_.name for state_ in SL]
            ret.append(retSL)
        return ret

    def minimise(self):
        self.removeUnreachable()
        print(self)
        PI_0 = [[],[]]

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
        mDFA_STS = []
        for SL in curPartition:
            # each SL will be a state in mDFA
            mDFA_names.append("".join([state_.name for state_ in SL]))
            mDFA_STS.append(self._make_STS(SL[0], curPartition))

        for stateName, state_STS in zip(mDFA_names, mDFA_STS):
            STS_transitions = list(state_STS.split("__")) 
            SNT_valueDict = {}
            inpSym_setIdx_tupleList = []
            for STS_transition in STS_transitions:
                inpSym_setIdx_tupleList.append( ( STS_transition.split("_")[0], int(STS_transition.split("_")[1]) ) )
            for transitionTuple in inpSym_setIdx_tupleList:
                SNT_valueDict[transitionTuple[0]] = mDFA_names[transitionTuple[1]]
            mDFA_SNT[stateName] = SNT_valueDict

        mDFA_initial = mDFA_names[self._findSetIdxOf(self.initialState, curPartition)]
        mDFA_finals = list( { mDFA_names[self._findSetIdxOf(finalState_, curPartition)] for finalState_ in self.finals} )
        self.define(mDFA_SNT, mDFA_initial, mDFA_finals)

