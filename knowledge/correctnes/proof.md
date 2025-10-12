### Notes
1. Language is enriched by additional set of consts $c_d$ for $d=0, 1, \dots$ and by additional set of consts 
$sk_r$ where $r$ is an arbitrary sequence of natural numbers.

1. $\alpha(x/\tau)$ is admissible iff no free
occurrence of $x$ in $\alpha$ is in the range of a quantifier that binds any variable which
appears in $\tau$.
1. For any sequences of natural numbers $r_1, r_2$, inequalities $r_1 < r_2$ and $r_1 \leq r_2$ are considered in lexicographical order.
1. We use Python convention to denote sequences as e.g. $[0, 2, 3]$, if $r$ is a sequence of natural numbers, then by $*r$ we denote all numbers from this sequence comma separated.
So if $r=[0,1,2]$, then $[*r, 3] = [0, 1, 2, 3]$.
1. For any sequence of natural numbers $r$, we define $d(r) = |r| - 1$.

<h3 id="axiom-schema">Axioms Schema</h3>
1. LEM: $\alpha \vee \neg\alpha$
2. IMP: $\alpha \to (\beta\to\alpha)$
3. ANL: $\alpha \wedge \beta \to \alpha$
4. ANR: $\alpha \wedge \beta \to \beta$
5. AND: $\alpha \to (\beta \to (\alpha \wedge \beta))$
6. ORL: $\alpha \to \alpha \vee \beta$
7. ORR: $\beta \to \alpha \vee \beta$
8. DIS: $(\alpha \to \gamma) \to ((\beta \to \gamma) \to (\alpha \vee \beta \to \gamma))$
9. CON: $\neg \alpha \to (\alpha \to \beta)$
10. IFI: $(\alpha \to \beta)\to((\beta\to\alpha)\to(\alpha\leftrightarrow\beta))$
11. IFO: $(\alpha\leftrightarrow\beta) \to (\alpha\to\beta) \wedge (\beta\to\alpha)$
12. ALL: $(\forall x. p) \to p(x/\tau)$ where $\tau$ is an arbitrary term and $p(x/\tau)$ is admissible.
13. EXT: $p(x/\tau) \to \exists x.p$ where $\tau$ is an arbitrary term and $p(x/\tau)$ is admissible.

<h3 id="rules-schema">Rules Schema</h3>
1. MOD: $p \to q,\; p \vdash q$
2. GEN: $p \vdash \forall x.p$
3. CTV: $p(x/c_d)\vdash \forall x.p$
4. SKO: $\exists x.p \vdash p(x/sk_r)$

<h3 id="proof-definition">Definition of correct proof</h3>

If $(r, B, s, f)$ is a correct proof of $f$ iff

$s$ is a sequence of $(r_i, m_i, s_i, f_{r_i})$ for $i=0, \cdots, k$ such that
$r_i = [*r, i]$, $m_i\in \{A, B, R, T\}$ and 

1. For any $sk_\rho$ in formula $f_{r_i}$, we have $\rho \leq r_i$.
2. For any $c_d$ in formula $f_{r_i}$, we have $d \leq d(r_i)$.  
1. For any $i$ such that $m_i = T$, we have $s_i=[]$ and $f_{r_i}$ 
belongs to <i>Axioms Schema</i>.
1. For any $i$ such that $m_i = R$, we have $s_i=[]$ 
and $f_{r_i}$ can be obtained by some rule from <i>Rules Schema</i> 
applied on some formulas from  $\{f_{\rho}:\rho < r_i\}$.
   1. For CTV, we have $d = d(r_i)$
1. For any $i$ such that $m_i = A$, we have $i=0$, $s_i=[]$ 
and $f_{r_i}$ is an arbitrary formula, 
such that for any $c_d$ in $f_{r_i}$, we have $d < d(r_i)$.
1. For $m_0 = A$, we have $f = \ulcorner f_{r_0} \to f_{r_k} \urcorner$. 
1. For $m_0 \not= A$, we have $f=f_{r_k}$.
1. For $m_i = B$, we have $(r_i, m_i, s_i, f_{r_i})$ is a correct proof of $f_{r_i}$.

<h3 id="consequence"> Consequence</h3>

$f \in Cn_R$ iff there is $s$ such that $([], B, s, f)$ is a correct proof of $f$.