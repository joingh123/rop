#!/bin/sh
gcc -fno-stack-protector -z execstack vulnerable_basic.c -o vb
