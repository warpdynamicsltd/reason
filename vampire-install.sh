#!/bin/bash

cd repositories/vampire || exit
mkdir build
cd build || exit
CC=/usr/bin/clang CXX=/usr/bin/clang++ cmake ..
make -j4
chmod 777 ./vampire
mkdir -p ../../../reason/assets/bin
cp ./vampire ../../../reason/assets/bin

