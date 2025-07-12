#!/bin/bash

dune build
rm -f ../reason/assets/bin/kernel
cp _build/install/default/bin/kernel ../reason/assets/bin