#!/usr/bin/env bash
set -e
export PYTHONDONTWRITEBYTECODE=1
python3 tests/test_nexo_hardware_arena.py
python3 experiments/run_full_article_benchmarks.py
python3 experiments/run_adversarial_torture_suite.py
