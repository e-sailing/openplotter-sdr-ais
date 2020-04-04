#!/bin/bash
rtl_fm -f  161975000 -g 24 -p $1 -s  48k | aisdecoder -h localhost -p 10110 -a file -c mono -d -f /dev/stdin