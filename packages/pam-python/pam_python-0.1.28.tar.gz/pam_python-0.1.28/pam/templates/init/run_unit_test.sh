#!/bin/bash
# Run unittest for mac & linux shell

if [ -n "$1" ]; then
  python -m unittest discover -s "$1" -p "test_*.py"
else
  python -m unittest discover
fi