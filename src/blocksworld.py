from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.formatter import domain_to_string, problem_to_string
from pddl.requirements import Requirements
from pddl import parse_domain, parse_problem
import itertools

import FSSP.pddlSample

parsedDomain = parse_domain('blocksworld (1).pddl')
parsedProblem = parse_problem('pb3.pddl')

print(domain_to_string(parsedDomain))
print(problem_to_string(parsedProblem))

"""

This class will act as a Node in the planning graph

"""


class Node():
    # will include the current state of domain
    # constants[], predicates[], childNode[]
    con = []  # ["a", "b", "c"] can be in any order
    # Could inplement map like so {"a" : type1, "b" : type1, "c" : type1}
    literals = []  # include variables in the form (p1 x, y, z)
    children = []  # Nodes that can be attained from actions

    def __init__(self, domain, problem):  # Use for start node
        self.domain = domain
        self.problem = problem

    def startNode(self):
        self.con = self.generateConstantsFromStart(self.problem)  # Get from problem.constants
        self.literals = self.generateLiteralsFromStart(self.problem)  # Get from problem.init
        self.children = self.generateChildrenFromActions(self.domain)  # generate from actions.domain

    def childNode(self, con, literals):
        self.con = con
        self.literals = literals
        self.children = []  # this isn't working so children nodes get no kids

    # TODO Return the name of the action along with corresponding constant, this will be for returning the path

    def getLiterals(self):
        return self.literals

    def setCons(self, cons):
        self.con = cons

    """
    return con as a list (ex. ["a", "b", "c"])
    """

    def generateConstantsFromStart(self, problem) -> list:
        variables = []
        x = problem.objects
        d = list(x)
        for elm in d:  # This is RNG what the order is for some reason
            variables.append(elm.name)
        # TODO return ["a", "b", "c"] or {"a" : type, "b": type, "c" : type}
        return variables  # Returns ["a", "b", "c"]

    # DONE
    def generateLiteralsFromStart(self, problem) -> list:
        state = []
        for pred in problem.init:
            state.append(pred)

        listOfList = []
        for pre in state:
            strPre = str(pre)
            listOfList.append(strPre)
        # TODO return ['(p1 a b c)', '(not (p2 b c))']
        return listOfList  # returns ['(p1 a b c)', '(not (p2 b c))']

    """

    Takes in any combination of literals and generates turns those literals into usable keys for the map that assigns
    a predicate to a effect from an action

    """

    def generateChildrenFromActions(self, domain):
        children = []
        groundedLiterals = self.groundList(self.literals)  # TODO [["(p1 a b c)", "not(p2 b c)"], ["not(p2 b c)", "(p1 a b c)"]]

        for cons in self.groundList(self.con):  # For every possible constant
            litMap = self.generatePredicatesFromAction(domain, cons)
            for lit in self.turnLiteralIntoKey(groundedLiterals):
                if litMap.get(lit) is not None:
                    effect = litMap.get(lit)
                    newNode = Node(self.domain, self.problem)
                    newNode.childNode(self.getConstantsFromEffects(effect), effect)
                    children.append(newNode)

        # Use the grounded variables as list to create action predicates
        # for loop checks if the current actions predicates match the literals for this node
        # if predicate == literal
        # create new node and add it to children
        return children

    def turnLiteralIntoKey(self, literals : list):
        #literals is a list of list containing string
        keyList = []
        for i in range(len(literals)):  # TODO this turns ["(p1 a b c)", "not(p2 b c)"] -> "(p1 a b c),not(p2 b c),"
            # TODO this doesn't work if childNode is generating children
            literalKey = ""
            for j in range(len(literals[i])):
                literalKey += literals[i][j]
                literalKey += ","
            keyList.append(literalKey)
        return keyList


    # This will create any combination of constants and put them into a list
    def groundList(self, newList) -> list:
        permute = itertools.permutations(newList)
        groundList = []
        # Iterate over all permutations
        for i in permute:
            consList = []
            # Convert the current
            # permutation into a list
            permutelist = list(i)

            # list separated by spaces
            for j in permutelist:
                consList.append(j)
            groundList.append(consList)

        # TODO implement so each list goes from ["a", "b", "c"] -> any combination of the constants
        return groundList

    def generatePredicatesFromAction(self, domain, con: list):
        param = {}  # {'?x', '?y', '?z'} This will be an issue when there is more than one action, set
        pre = []  # ['(p1 ?x ?y ?z)', '(not (p2 ?y ?z))'] This will be an issue when there is more than one action
        effect = []  # ["(p2 ?y ?z)"]
        for action in domain.actions:
            par = action.parameters
            for p in par:
                param.append(str(p))
            tup = action.precondition
            pre.append(str(tup))
            eff = action.effect  # for e in eff:
            effect.append(str(eff))

        # TODO implemented to produce ['(p1 ?x ?y ?z)', '(not (p2 ?y ?z))'] <- this is in pre
        varToCon = {}
        if (len(param) != len(con)):
            return
        for i in range(len(param)):
            varToCon.__setitem__(param[i], con[i])

        newPred = []
        count = 0
        # TODO manually recreate string representation of literal
        # TODO turn ['(p1 ?x ?y ?z)', '(not (p2 ?y ?z))'] -> ["(p1 a b c)", "(not (p2 b c))"]

        for word in pre:
            literalsWithSpaces = []
            count = word.count(")")
            newestWord = []
            newWord = word[:len(word) - count].split(" ")
            for j in range(len(newWord)):
                if varToCon.get(newWord[j]) is None:
                    newestWord.append(newWord[j])
                else:  # This checks if there is a matching variable and constant
                    newestWord.append(varToCon.get(newWord[j]))
            for applySpace1 in newestWord:
                literalsWithSpaces.append(applySpace1)
                if applySpace1 is not newestWord[len(newestWord) - 1]:  # if it's not the last word
                    literalsWithSpaces.append(" ")
            newestString = "".join(map(str, literalsWithSpaces))
            for i in range(count):
                newestString += ")"
            newPred.append(newestString)
        pre = newPred
        # TODO break each string into a list p1 -> ["(", "p1", "?x", "?y", "z?" ")"] to ["(", "p1", "a", "b", "c", ")"]
        # TODO then combine the list to  produce "(p1 a b c)"
        newEff = []
        theNewestString = []
        count = 0
        for word in effect:
            newestWord = []
            count = word.count(")")
            predicateList = word[:len(word) - count].split(" ")
            for i in range(len(predicateList)):
                if varToCon.get(predicateList[i]) is None:
                    newestWord.append(predicateList[i])
                else:  # This checks if there is a matching variable and constant
                    newestWord.append(varToCon.get(predicateList[i]))
            for applySpace2 in newestWord:
                theNewestString.append(applySpace2)
                if applySpace2 is not newestWord[len(newestWord) - 1]:  # if it's not the last word
                    theNewestString.append(" ")
            newestString = "".join(map(str, theNewestString))
            for i1 in range(count):
                newestString += ")"
            newEff.append(newestString)
        effect = newEff
        # TODO replace keys with values in predicate

        # TODO Take each item in pred and combine it ["(p1 a b c)", "not(p2 b c)"] -> "(p1 a b c),(not(p2 b c)),"
        predEff = {}
        singleStrPred = ""
        for i2 in range(len(pre)):  # only adding the second predicate
            if isinstance(pre[i2], list):
                for j in range(len(pre[i2])):
                    singleStrPred += pre[i2][j]
                    singleStrPred += ","
            else:
                singleStrPred += pre[i2]
                singleStrPred += ","
            singleStrEffect = ""
            # Need to create a special case when effects is more than one string
        for l1 in range(len(effect)):
            if isinstance(pre[l1], list):
                for k in range(len(effect)):
                    singleStrEffect += effect[l1][k]
            else:
                singleStrEffect += effect[l1]
        predEff.__setitem__(singleStrPred, singleStrEffect)

        # TODO predEff -> {"(p1 a b c),(not(p2 b c))," : "(p2 b c)"}

        return predEff

    def getConstantsFromEffects(self, effect: str):
        cons = []
        word = effect.replace(")", "")
        conList = word.split(" ")
        for i in range(1, len(conList)):
            cons.append(conList[i])
        return cons

    def getChildren(self):
        return self.children

def goalState(problem):
    return str(problem.goal)

def algorithm(domain, problem):
    initialProblem = Node(domain, problem)  # pi <- {(s0, null)}
    initialProblem.startNode()
    queue = []
    queue.append(initialProblem)
    while len(queue) > 0:
        current = queue.pop(0)
        print(current.getLiterals())
        print(goalState(problem))
        if current.getLiterals() == (goalState(problem)):  # Will have to iterate and check over each problem
            print("Plan Successful")
            return initialProblem  # This will be replaced with string of plan
        for neighbor in current.getChildren():  # This is where you would get children from actions
            queue.append(neighbor)
    print("Plan Failed")

if __name__ == '__main__':
    print("Testing Algorithm: ")
    algorithm(parsedDomain, parsedProblem)

