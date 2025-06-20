#!/bin/bash

cd repositories/vampire
mkdir build
cd build
CC=/usr/bin/clang CXX=/usr/bin/clang++ cmake ..
make -j4
chmod 777 ./vampire
mkdir -p ../../../reason/assets/bin
cp ./vampire ../../../reason/assets/bin

