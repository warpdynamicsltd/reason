<h3 id="universal-constant">Definition: <b>universal constant</b></h3>

$a\in\mathcal{C}$ is an universal constant with respect to the set of formulas $\Gamma$ iff.

For any formula $\alpha(a)\in\Gamma$, we have $\Gamma\models\forall x. \alpha(x) $.

<h3 id="universal-constat-tautology">Lemma: tautologies with constants</h3>

If $a\in\mathcal{C}$ and $\models\alpha(a)$, then $\models  \forall x. \alpha(x) $.

<b>Proof.</b> Let $\mathcal{M}$ be an arbitrary model. Take an arbitrary element $d\in D^\mathcal{M}$. Let $\mathcal{M}'$ be a model which differs from model $\mathcal{M}$ just by assignement of constant $a$, namely $[a]^{\mathcal{M}'} = d$. Since $\models  \alpha(a) $, $\mathcal{M}'\models  \alpha(a) $. Since $d\in D^\mathcal{M}$ was arbitrary, we have $\mathcal{M}\models  \forall x. \alpha(x) $. Since $\mathcal{M}$ was arbitrary, we showed $\models  \forall x. \alpha(x) $.

<h3 id="universal-constant">Theorem: <b>universal constant</b></h3>

If $a\in\mathcal{C}$ is an universal constant with respect to $\Gamma$, then for any $\Gamma\models  \beta(a) $, we have $\Gamma\models \forall x. \beta(x) $.

<b>Proof.</b> Since $\Gamma\models \beta(a) $, we have some $ \alpha_i(a)  \in\Gamma$ which contains constant $a$ and possibly some $\gamma_i\in\Gamma$ which do not contain constant $a$ such that

$$\models  \alpha_1(a) \wedge \dots \wedge \alpha_n(a) \wedge \gamma_1 \wedge \dots \wedge \gamma_k \to \beta(a) $$

Let $\gamma$ denotes $\gamma_1 \wedge \dots \wedge \gamma_k$. By Lemma [tautologies with constants](universal-constat-tautology)

$$\models  \forall x. \ \alpha_1(x) \wedge \dots \wedge \alpha_n(x) \wedge \gamma \to \beta(x) ,$$

$$\models  \forall x. \ \neg\alpha_1(x) \vee \dots \vee \neg\alpha_n(x) \vee \neg\gamma \vee \beta(x) ,$$

$$\models  \forall x. \ (\neg\alpha_1(x) \vee \dots \vee \neg\alpha_n(x) \vee \neg\gamma) \vee (\forall x.\beta(x)) ,$$

$$\models  \exists x. \ (\neg\alpha_1(x) \vee \dots \vee \neg\alpha_n(x) \vee \neg\gamma) \vee (\forall x.\beta(x)) ,$$

$$\models  \neg\forall x.\alpha_1(x) \vee \dots \vee \neg\forall x.\alpha_n(x) \vee \neg\gamma \vee (\forall x.\beta(x)) .$$

But by Definition [universal constant](universal-constant), $\Gamma\models \forall x.\alpha_i(x)$ and of course $\Gamma\models \gamma$, thus
$$\Gamma \models  \forall x. \beta(x) .$$

<h3 id="corollary-universal-constant">Corollary: <b>invariance of universal constant</b></h3>

If $a\in\mathcal{C}$ is an universal constant with respect to $\Gamma$ and $\Gamma\models  \beta(a) $, then $a$ is an universal constant with respect to $`\Gamma\cup \{ \beta(a) \}`$.






