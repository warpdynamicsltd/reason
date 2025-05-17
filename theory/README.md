<h3 id="universal-constant">Definition: <b>universal constant</b></h3>

$a\in\mathcal{C}$ is an universal constant with respect to the set of formulas $\Gamma$ iff.

For any formula $\ulcorner \alpha(a) \urcorner \in\Gamma$, we have $\Gamma\models \ulcorner \forall x. \alpha(x) \urcorner$.

<h3 id="universal-constat-tautology">Lemma: tautologies with constants</h3>

If $a\in\mathcal{C}$ and $\models \ulcorner \alpha(a) \urcorner$, then $\models \ulcorner \forall x. \alpha(x) \urcorner$.

<b>Proof.</b> Let $\mathcal{M}$ be an arbitrary model. Take an arbitrary element $d\in D^\mathcal{M}$. Let $\mathcal{M}'$ be a model which differs from model $\mathcal{M}$ just by assignement of constant $a$, namely $[a]^{\mathcal{M}'} = d$. Since $\models \ulcorner \alpha(a) \urcorner$, $\mathcal{M}'\models \ulcorner \alpha(a) \urcorner$. Since $d\in D^\mathcal{M}$ was arbitrary, we have $\mathcal{M}\models \ulcorner \forall x. \alpha(x) \urcorner$. Since $\mathcal{M}$ was arbitrary, we showed $\models \ulcorner \forall x. \alpha(x) \urcorner$.

<h3 id="universal-constant">Theorem: <b>universal constant</b></h3>

If $a\in\mathcal{C}$ is an universal constant with respect to $\Gamma$, then for any $\Gamma\models \ulcorner \beta(a) \urcorner$, we have $\Gamma\models\ulcorner \forall x. \beta(x) \urcorner$.

<b>Proof.</b> Since $\Gamma\models\ulcorner \beta(a) \urcorner$, we have some $\ulcorner \alpha_i(a) \urcorner \in\Gamma$ which contains constant $a$ and possibly some $\gamma_i\in\Gamma$ which do not contain constant $a$ such that

$$\models \ulcorner \alpha_1(a) \wedge \dots \wedge \alpha_n(a) \wedge \gamma_1 \wedge \dots \wedge \gamma_k \to \beta(a) \urcorner$$

Let $\gamma$ denotes $\gamma_1 \wedge \dots \wedge \gamma_k$. By Lemma [tautologies with constants](universal-constat-tautology)

$$\models \ulcorner \forall x. \; \alpha_1(x) \wedge \dots \wedge \alpha_n(x) \wedge \gamma \to \beta(x) \urcorner,$$

$$\models \ulcorner \forall x. \; \neg\alpha_1(x) \vee \dots \vee \neg\alpha_n(x) \vee \neg\gamma \vee \beta(x) \urcorner,$$

$$\models \ulcorner \forall x. \; (\neg\alpha_1(x) \vee \dots \vee \neg\alpha_n(x) \vee \neg\gamma) \vee (\forall x.\beta(x)) \urcorner,$$

$$\models \ulcorner \exists x. \; (\neg\alpha_1(x) \vee \dots \vee \neg\alpha_n(x) \vee \neg\gamma) \vee (\forall x.\beta(x)) \urcorner,$$

$$\models \ulcorner \neg\forall x.\alpha_1(x) \vee \dots \vee \neg\forall x.\alpha_n(x) \vee \neg\gamma \vee (\forall x.\beta(x)) \urcorner.$$

But by Definition [universal constant](universal-constant), $\Gamma\models \forall x.\alpha_i(x)$ and of course $\Gamma\models \gamma$, thus
$$\Gamma \models \ulcorner \forall x. \beta(x) \urcorner.$$

<h3 id="corollary-universal-constant">Corollary: <b>invariance of universal constant</b></h3>

If $a\in\mathcal{C}$ is an universal constant with respect to $\Gamma$ and $\Gamma\models \ulcorner \beta(a) \urcorner$, then $a$ is an universal constant with respect to $\Gamma\cup\{\ulcorner \beta(a) \urcorner\}$.






