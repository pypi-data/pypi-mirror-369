## 构建依赖包

```基础命令
python -m pip install twine  -i https://mirrors.tencent.com/pypi/simple
pip install wheel setuptools -i https://mirrors.tencent.com/pypi/simple
python setup.py sdist bdist_wheel
python -m build
pip install .
pip install -e .
pip install -e .[dev]
```

```shell 构建命令
#rm -rf './dist'
#python -m build
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```
