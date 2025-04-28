#!/bin/bash

for i in {1..10}
do
    echo "========================="
    echo "Running test$i.txt"
    echo "========================="
    python3 dual.py "test$i.txt"
    echo
    python3 q1.py "segs$i.txt" "out$i.txt" "test$i.txt"
done
