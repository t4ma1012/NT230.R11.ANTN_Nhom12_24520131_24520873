#!/bin/bash
set -e
make clean
make
printf '\n===== HEX =====\n'
xxd -g 1 payload.bin
printf '\n===== DISASSEMBLY =====\n'
ndisasm -b 64 payload.bin
printf '\n===== DEMO =====\n'
./task11_demo
