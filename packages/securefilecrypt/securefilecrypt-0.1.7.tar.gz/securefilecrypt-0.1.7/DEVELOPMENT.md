# Development tasks

## Build and install locally for testing

Commands to build package and install it from local distribution file:

```
pip uninstall securefilecrypt
rmdir /s /q dist\
python -m build
pip install dist\securefilecrypt-<version>-py3-none-any.whl
```

## Build and deploy to PyPI

Commands to build package, deploy to PyPI and install it from there:

```
pip uninstall securefilecrypt
rmdir /s /q dist\
python -m build
python -m twine upload dist/*
pip install securefilecrypt==<version>
```
