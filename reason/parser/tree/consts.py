from types import SimpleNamespace

NEG = "NEG"
AND = "AND"
OR = "OR"
IMP = "IMP"
IFF = "IFF"
FORALL = "FORALL"
EXISTS = "EXISTS"
IN = "IN"
EQ = "EQ"
CONJUNCTION = "CONJUNCTION"
INTERSECT = "INTERSECT"
UNION = "UNION"
INCLUDES = "INCLUDES"
SEQ = "SEQ"
SET = "SET"
SELECT = "SELECT"
MAPS = "MAPS"

const = SimpleNamespace()
const.NEG = NEG
const.AND = AND
const.OR = OR
const.IMP = IMP
const.IFF = IFF
const.FORALL = FORALL
const.EXISTS = EXISTS
const.IN = IN
const.EQ = EQ
const.CONJUNCTION = CONJUNCTION
const.INTERSECT = INTERSECT
const.UNION = UNION
const.INCLUDES = INCLUDES
const.SEQ = SEQ
const.SET = SET
const.SELECT = SELECT
const.MAPS = MAPS

# PROGRAM

ATOMIC_AXIOM = "ATOMIC_AXIOM"
ASSERTION = "ASSERTION"
DEFINITION = "DEFINITION"
ASSUMPTION = "ASSUMPTION"
CONCLUSION = "CONCLUSION"
CONST_DECLARATION = "CONST_DECLARATION"
CONST_USE_DECLARATION = "CONST_USE_DECLARATION"
CONST_DECLARATION_WITH_CONSTRAIN = "CONST_DECLARATION_WITH_CONSTRAIN"
CONST_USE_DECLARATION_WITH_CONSTRAIN = "CONST_USE_DECLARATION_WITH_CONSTRAIN"
CONTEXT_BLOCK = "CONTEXT_BLOCK"
THEOREM_CONTEXT_BLOCK = "THEOREM_CONTEXT_BLOCK"

INCLUDE_FILE = "INCLUDE_FILE"

const.ATOMIC_AXIOM = ATOMIC_AXIOM
const.ASSERTION = ASSERTION
const.DEFINITION = DEFINITION
const.ASSUMPTION = ASSUMPTION
const.CONCLUSION = CONCLUSION
const.CONST_DECLARATION = CONST_DECLARATION
const.CONST_USE_DECLARATION = CONST_USE_DECLARATION
const.CONST_DECLARATION_WITH_CONSTRAIN = CONST_DECLARATION_WITH_CONSTRAIN
const.CONST_USE_DECLARATION_WITH_CONSTRAIN = CONST_USE_DECLARATION_WITH_CONSTRAIN
const.CONTEXT_BLOCK = CONTEXT_BLOCK
const.THEOREM_CONTEXT_BLOCK = THEOREM_CONTEXT_BLOCK

const.INCLUDE_FILE = INCLUDE_FILE
