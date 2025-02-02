# REASON

## Installation guide

Clone the Reason Repository by `git clone --recursive https://github.com/warpdynamicsltd/reason.git`. 
This will clone Reason with dependency repositories

1. `repositories/lark`
2. `repositories/vampire`

If you want to install `reason` package in your local Python environment 
with the most up to date versions of dependencies, you should follow the steps below:

1. Go to the root folder of Reason repository.
2. Build binary for Vampire by `./vampire-install.sh`. This will run `cmake` over Vampire codes and next `make` to build it from sources and copy vampire binary to `reason/assets/bin`.
3. One possible way to install `reason` package in your local Python environment:
   1. Install `uv` package manager by e.g. `curl -LsSf https://astral.sh/uv/install.sh | sh`.
   2. Run `uv sync` on the level of the project root directory.
   3. Run `uv run task test` to run tests to verify if your installation is successful.

If you know what you are doing you may skip steps 1 - 3 and e.g. install lark by `pip install lark` 
and/or get vampire binary compiled somewhere else and copy it manually to `reason/assets/bin`.

## Usage Example

Mind that the code below might run for several seconds.

```python
from reason.vampire import Vampire
from reason.parser import Parser
from reason.core.theory import Theory

reason_parser = Parser()
vampire_prover = Vampire()

ZFC = Theory(parser=reason_parser, prover=vampire_prover)

ZFC.add_const("∅")

ZFC.add_axiom("∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y)", name="a0")
ZFC.add_axiom("empty(e) ⟷ (∀(x) ~(x ∈ e))", name="d1")
ZFC.add_axiom("empty(∅)", name="a1")
ZFC.add_axiom("∀(x, z) z ∈ {x} ⟷ z = x", name="a3")
ZFC.add_axiom("∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y", name='a4')
ZFC.add_axiom("∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y", name='a5')
ZFC.add_axiom("∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y)", name='d2')
ZFC.add_axiom("∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅)", name='a6')
ZFC.add_axiom("{a, b} = {a} ∪ {b}", name='d3')
ZFC.add_axiom("(a, b) = {a, {a, b}}", name='d4')

print(ZFC("∀(x) empty(x) → x = ∅"))
print(ZFC("∀(x, y) {x} = {y} → x = y"))
print(ZFC("∀(x, y) x ∩ y ⊂ x ∪ y"))
print(ZFC("(a, b) = (c, d) → a = c ∧ b = d"))
```

The output of the above should be:

```
True
True
True
True
```

To learn more about reason study more examples in [Examples](examples) directory.