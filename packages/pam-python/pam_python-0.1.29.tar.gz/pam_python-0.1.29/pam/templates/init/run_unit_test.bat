:: Run unittest for windows CMD

@echo off
SETLOCAL

IF "%~1"=="" (
    python -m unittest discover
) ELSE (
    python -m unittest discover -s %~1 -p "test_*.py"
)
