# Run unittest for windows powershell

param(
    [string]$TestDir
)

if ($TestDir) {
    python -m unittest discover -s $TestDir -p "test_*.py"
} else {
    python -m unittest discover
}
