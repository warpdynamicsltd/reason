from reason.core.fof_types import *

def And(a, b):
    return LogicConnective("AND", a, b)

def Or(a, b):
    return LogicConnective("OR", a, b)

def Implies(a, b):
    return LogicConnective("IMP", a, b)

def Iff(a, b):
    return LogicConnective("IFF", a, b)

def Not(a):
    return LogicConnective("NEG", a)

def Forall(x, f):
    return LogicQuantifier("FORALL", Variable(x), f)

def Exists(x, f):
    return LogicQuantifier("EXISTS", Variable(x), f)