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

1. LEM. $\alpha \vee \neg\alpha$
2. IMP. $\alpha \to (\beta\to\alpha)$
3. ANL. $\alpha \wedge \beta \to \alpha$
4. ANR. $\alpha \wedge \beta \to \beta$
5. AND. $\alpha \to (\beta \to (\alpha \wedge \beta))$
6. ORL. $\alpha \to \alpha \vee \beta$
7. ORR. $\beta \to \alpha \vee \beta$
8. DIS. $(\alpha \to \gamma) \to ((\beta \to \gamma) \to (\alpha \vee \beta \to \gamma))$
9. CON. $\neg \alpha \to (\alpha \to \beta)$
10. IFI. $(\alpha \to \beta)\to((\beta\to\alpha)\to(\alpha\leftrightarrow\beta))$
11. IFO. $(\alpha\leftrightarrow\beta) \to (\alpha\to\beta) \wedge (\beta\to\alpha)$
12. ALL. $(\forall x. p) \to p(x/\tau)$ where $\tau$ is an arbitrary term and $p(x/\tau)$ is admissible.
13. EXT. $p(x/\tau) \to \exists x.p$ where $\tau$ is an arbitrary term and $p(x/\tau)$ is admissible.

<h3 id="rules-schema">Rules Schema</h3>

1. MOD. $p \to q,\; p \vdash q$
2. GEN. $p \vdash \forall x.p$
3. CTV. $p(x/c_d)\vdash \forall x.p$
4. SKO. $\exists x.p \vdash p(x/sk_\sigma)$

<h3 id="proof-definition">Recursive definition of correct proof</h3>

If $(r', B, s, f)$ is a correct proof of $f$ iff

$s$ is a sequence of $(r, m_r, s_r, f_r)$ such that
$r = [*r', i]$ for $i=0, \cdots, k$ with $m_r\in \{A, B, R, T\}$ and: 

1. For any $sk_\rho$ in formula $f_r$, we have $\rho \leq r$.
2. For any $c_d$ in formula $f_r$, we have $d \leq d(r)$.  
1. For any $r$ such that $m_r = T$, we have $s_r=[]$ and $f_r$ 
belongs to <i>Axioms Schema</i>.
   
1. For any $r$ such that $m_r = R$, we have $s_r=[]$ 
and $f_r$ can be obtained by some rule from <i>Rules Schema</i> 
applied on some formulas from  $\{f_{\rho}:\rho < r\}$.
   1. For rule CTV, we have additional constrain $d = d(r)$
   1. For rule SKO, we have additional constrain $\sigma = r$.
   1. For rule GEN, we have additional constrain that
   $x \not\in\cup\left\{free(f_\rho): \rho < r \text{ and } m_\rho=A\right\}$.
1. For any $r$ such that $m_r = A$, we have $i=0$, $s_r=[]$ 
and $f_r$ is an arbitrary formula, 
such that for any $c_d$ in $f_r$, we have $d < d(r)$.
1. For $m_{[*r',0]} = A$, we have $f = \ulcorner f_{[*r',0]} \to f_{[*r', k]} \urcorner$. 
1. For $m_{[*r',0]} \not= A$, we have $f=f_{[*r', k]}$.
1. For $m_r = B$, we have $(r, m_r, s_r, f_r)$ is a correct proof of $f_r$.

<h3 id="consequence"> Consequence</h3>

$f \in Cn_R$ iff there is $s$ such that $([], B, s, f)$ is a correct proof of $f$.