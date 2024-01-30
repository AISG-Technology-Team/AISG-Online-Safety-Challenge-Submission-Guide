#!/bin/bash

cat ../local_test/test_stdin/stdin_local.csv | python3 main.py \
    1>../local_test/test_output/stdout.csv 2>../local_test/test_output/stderr.csv