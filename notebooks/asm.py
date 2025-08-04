#%%
from reason.core.language import Language
from reason.kernel import Kernel
from reason.kernel.proof import *
from reason.kernel.statement import *
from reason.core.fof_logic import *

L = Language()

proof = BlockStmt(
    ref=Ref([]),
    statements=[
        Assumption(
            ref=Ref([0]),
            formula=L("P")
        ),
        RuleStmt(
            ref=Ref([1]),
            label="IDN",
            refs=[Ref([0])],
            terms=[],
            formula=L("P")
        )
    ],
    formula=L("P → P")
)

proof2 = BlockStmt(
    ref=Ref([]),
    statements=[
        Assumption(
            ref=Ref([0]),
            formula=L("P")
        ),
        BlockStmt(
            ref=Ref([1]),
            statements=[
                Assumption(
                    ref=Ref([1, 0]),
                    formula=L("Q")
                ),

                RuleStmt(
                    ref=Ref([1, 1]),
                    label="IDN",
                    refs=[Ref([0])],
                    terms=[],
                    formula=L("P")
                )
            ],
            formula=L("Q → P")
        )
    ],
    formula=L("P → (Q → P)")
)

proof3 = BlockStmt(
    ref=Ref([]),
    statements=[
        Assumption(
            ref=Ref([0]),
            formula=L("P")
        ),
        BlockStmt(
            ref=Ref([1]),
            statements=[
                Assumption(
                    ref=Ref([1, 0]),
                    formula=L("A")
                ),
                RuleStmt(
                    ref=Ref([1, 1]),
                    label="IDN",
                    refs=[Ref([1, 0])],
                    terms=[],
                    formula=L("A")
                )
            ],
            formula=L("A → A")
        ),
        BlockStmt(
            ref=Ref([2]),
            statements=[
                Assumption(
                    ref=Ref([2, 0]),
                    formula=L("Q")
                ),
                RuleStmt(
                    ref=Ref([2, 1]),
                    label="IDN",
                    refs=[Ref([1])],
                    terms=[],
                    formula=L("A → A")
                )
            ],
            formula=L("Q → (A → A)")
        )
    ],
    formula=L("P → (Q → (A → A))")
)

proof4 = BlockStmt(
    ref=Ref([]),
    statements=[
        BlockStmt(
            ref=Ref([0]),
            statements=[
                Assumption(
                    ref=Ref([0, 0]),
                    formula=L("A")
                ),
                RuleStmt(
                    ref=Ref([0, 1]),
                    label="IDN",
                    refs=[Ref([0, 0])],
                    terms=[],
                    formula=L("A")
                )
            ],
            formula=L("A → A")
        ),
        BlockStmt(
            ref=Ref([1]),
            statements=[
                Assumption(
                    ref=Ref([1, 0]),
                    formula=L("Q")
                ),
                RuleStmt(
                    ref=Ref([1, 1]),
                    label="IDN",
                    refs=[Ref([0])],
                    terms=[],
                    formula=L("A → A")
                )
            ],
            formula=L("Q → (A → A)")
        )
    ],
    formula=L("Q → (A → A)")
)


proof5 = BlockStmt(
    ref=Ref([]),
    statements=[
        Assumption(
            ref=Ref([0]),
            formula=L("P")
        ),
        AxiomStmt(
            ref=Ref([1]),
            label="LEM",
            fofs=[L("P")],
            terms=[],
            formula=L("P or ~P")
        ),
        RuleStmt(
            ref=Ref([2]),
            label="IDN",
            refs=[Ref([1])],
            terms=[],
            formula=L("P or ~P")
        )
    ],
    formula=L("P → P or ~P")
)

f1 = Kernel.prove_tautology(proof)
f2 = Kernel.prove_tautology(proof2)
f3 = Kernel.prove_tautology(proof3)
f4 = Kernel.prove_tautology(proof4)
f5 = Kernel.prove_tautology(proof5)

# BEGIN()
# a_index = p_implies_p(L("P and Q"))
# p_index = ANL(L("P"), L("Q"))
# q_index = ANR(L("P"), L("Q"))
# a_p_and_q(p_index, q_index)
# f = END()
print(L.printer(f1))
print(L.printer(f2))
print(L.printer(f3))
print(L.printer(f4))
print(L.printer(f5))

# BEGIN()
# a = LEM(L("P"))
# b = IMP(GET_FORMULA(a), L("Q"))
# print(b, a)
# print(L.printer(GET_FORMULA(b)))
# print(L.printer(GET_FORMULA(a)))
# c = MOD(b, a)
# f = END()
# print(L.printer(f))
# print(L.printer(GET_FORMULA(c)))