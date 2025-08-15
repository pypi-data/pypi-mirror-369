from setuptools import setup, find_packages

setup(
    name="path_magician",          # 包名（必须唯一，PyPI上不能与现有包重复）
    version="0.1.2",         # 版本号（遵循语义化版本：主版本.次版本.修订号）
    author="Jiahuan",      # 作者名
    author_email="719481125@qq.com",  # 作者邮箱
    description="make path management easier",  # 包的简短描述
    packages=find_packages(),  # 自动发现所有Python包（即`my_tool`目录）
    classifiers=[             # 包的分类标签（帮助用户找到你的包，参考PyPI分类表）
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # 支持的Python最低版本
    install_requires=[],      # 包的依赖（如需要requests，就写["requests>=2.25.0"]）
)