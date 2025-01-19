#!/bin/bash

cd repositories/vampire
cmake .
make -j4
chmod 777 ./vampire
mkdir -p ../../reason/assets/bin
cp ./vampire ../../reason/assets/bin

