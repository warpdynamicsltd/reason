#!/bin/bash

eval $(opam env)
dune build
rm -f ../reason/assets/bin/kernel
cp _build/install/default/bin/kernel ../reason/assets/bin