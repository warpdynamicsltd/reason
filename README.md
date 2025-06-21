# REASON

## Installation guide

It is recommended to install <i>Reason</i> on Linux. 
Instruction below assumes Debian-based distribution, but you may adjust it to your favourite Linux distribution.

Clone the <i>Reason</i> repository by `git clone --recursive https://github.com/warpdynamicsltd/reason.git`. 
This will clone Reason with dependency repositories

1. `repositories/lark`
2. `repositories/vampire`

To install `reason` package in your local Python environment 
with the most up to date versions of dependencies, you should follow the steps below:

1. Most likely you will need to install:
   ```bash
   sudo apt install -y build-essential cmake clang zlib1g-dev libgmp-dev python3 curl
   ```
1. Go to the root folder of Reason repository.
2. Build binary for Vampire by `./vampire-install.sh`. This will run `cmake` over Vampire codes and next `make` to build it from sources and copy vampire binary to `reason/assets/bin`.
3. One possible way to install `reason` package in your local Python environment:
   1. Install `uv` package manager by e.g. `curl -LsSf https://astral.sh/uv/install.sh | sh`.
   2. Run `uv sync` on the level of the project root directory.
   3. Run `uv run task test` to run tests to verify if your installation is successful.

If you know what you are doing you may skip steps 1 - 3 and e.g. install lark by `pip install lark` 
and/or get vampire binary compiled somewhere else and copy it manually to `reason/assets/bin`.

## Usage Example

### examples/basic/example.rsn

```reason
axiom ∀(x, y) x = y ⟷ (∀(z) z ∈ x ⟷ z ∈ y);
axiom empty(e) ⟷ (∀(x) ~(x ∈ e));
axiom empty(∅);
axiom ∀(x, z) z ∈ {x} ⟷ z = x;
axiom ∀(x, y, z) z ∈ x ∪ y ⟷ z ∈ x ∨ z ∈ y;
axiom ∀(x, y, z) z ∈ x ∩ y ⟷ z ∈ x ∧ z ∈ y;
axiom ∀(x, y) x ⊂ y ⟷ (∀(z) z ∈ x → z ∈ y);
axiom ∀(x) ~(x = ∅) → (∃(y) y ∈ x ∧ y ∩ x = ∅);

let {a, b} = {a} ∪ {b};
let (a, b) = {a, {a, b}};

theorem ~(a ∈ b ∧ b ∈ a)
proof
  take a, b;
  assume a ∈ b;
  assume b ∈ a;

  take e;
  let e = {a, b};
  ~(a ∩ e = ∅);
  b ∩ e = ∅;
  then ~(a ∈ b);
qed;
```

You can run the above proof with:
```bash
reason examples/basic/example.rsn
```

The output of the above should end with something similar to the following.

```
QUOD ERAT DEMONSTRANDUM
proved in 0.045 seconds
```

To learn more about reason study more examples in [Examples](examples) directory.