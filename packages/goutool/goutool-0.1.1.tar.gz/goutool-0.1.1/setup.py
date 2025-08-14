from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="goutool",
    version="0.1.1",
    author="wl4837",
    author_email="wl4837@163.com",
    description="🐶 Python工具类库 更加快速的开发项目 便捷优雅的使用类库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/wl4837/goutool",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        "dev": ["pytest>=6.0", "twine>=3.0"],
    },
)