#!/bin/bash

cd repositories/ctxproof/CtxProof || exit


OPAM_ROOT="${OPAMROOT:-$HOME/.opam}"

already_init=false
# Check via CLI (fast) or fallback to file check
if opam switch show >/dev/null 2>&1; then
  already_init="true"
elif [ -f "$OPAM_ROOT/config" ]; then
  already_init="true"
fi


if [ "$already_init" != "true" ]; then
  OPAMYES=1 opam init --disable-sandboxing --no-setup
fi
eval $(opam env)
opam update
opam install . --deps-only -y
eval $(opam env)
dune build
dune test
rm -f ../../../reason/assets/bin/ctxproof || exit 1
cp _build/install/default/bin/ctxproof ../../../reason/assets/bin/ctxproof || exit 1