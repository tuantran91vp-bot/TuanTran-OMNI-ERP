$ErrorActionPreference = "Stop"

python -m unittest discover -s tests
python -m compileall src tests
