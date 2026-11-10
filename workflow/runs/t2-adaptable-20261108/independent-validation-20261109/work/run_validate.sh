#!/bin/bash
# Reproducible runner: 2-core pinned Dinov2 validation, memory measured by /usr/bin/time -v
cd "$(dirname "$0")"
/usr/bin/time -v -o validate_t2.time taskset -c 0,1 /mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python validate_t2.py > validate_t2.log 2> validate_t2.err
echo "python_exit=$?"
