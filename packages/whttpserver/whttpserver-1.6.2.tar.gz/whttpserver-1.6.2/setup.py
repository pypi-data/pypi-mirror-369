from setuptools import setup, find_packages

setup(
    name="whttpserver",      # PyPI 上的包名
    version="1.6.2",              # 版本号
    packages=find_packages(),    # 自动发现包
    include_package_data=True,  # 包含非 Python 文件
    package_data={
        "whttpserver": ["templates/*"],  # 包含 templates 下的所有文件
    },
    entry_points={
        "console_scripts": [
            "whttpserver=whttpserver.__main__:main",  # 命令行工具
        ],
    },
    install_requires=["flask"],         # 依赖项（如需要 Flask，可填 ["flask"]）
    author="Wang Junbo",
    author_email="wjbhnu@gmail.com",
    description="A simple HTTP server like `python -m http.server`",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://www.ddz.cool",
    classifiers=[                # PyPI 分类标签
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7",    # Python 版本要求
)