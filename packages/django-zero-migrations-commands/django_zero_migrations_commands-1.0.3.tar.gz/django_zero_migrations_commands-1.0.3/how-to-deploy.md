https://packaging.python.org/en/latest/tutorials/packaging-projects/

Set the new version number in pyproject.toml

then
```bash
rm -R dist
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
```
