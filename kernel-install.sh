#!/bin/bash

cd kernel || exit


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
opam install dune
./build.sh