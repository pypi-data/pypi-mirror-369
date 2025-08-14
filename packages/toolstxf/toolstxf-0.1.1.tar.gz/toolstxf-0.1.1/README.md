构建分发包
在项目根目录运行：
python -m pip install --upgrade build
python -m build
执行后会生成：
dist/
├── my_package-0.1.0-py3-none-any.whl
└── my_package-0.1.0.tar.gz
4. 上传到 PyPI
安装 Twine：
python -m pip install --upgrade twine
上传到测试 PyPI（推荐先测试）：
python -m twine upload --repository testpypi dist/*
测试 PyPI 地址：https://test.pypi.org/

测试安装：
pip install --index-url https://test.pypi.org/simple/ my_package
确认没问题后，上传到正式 PyPI：
python -m twine upload dist/*
正式 PyPI 地址：https://pypi.org/

5. 安装自己的包
pip install my_package
