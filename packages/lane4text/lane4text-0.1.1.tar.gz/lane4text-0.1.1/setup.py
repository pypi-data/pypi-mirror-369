from setuptools import setup, find_packages

setup(
    name="lane4text",
    version="0.1.1",
    packages=find_packages(include=['lane4text', 'lane4text.*']),  # <-- 包含子模块
    author="huangyongqi",
    description="带噪文本分类",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)