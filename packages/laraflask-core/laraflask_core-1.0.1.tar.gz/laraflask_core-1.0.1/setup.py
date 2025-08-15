from setuptools import setup, find_packages

setup(
    name="laraflask-core",
    version="1.0.1",
    author="Rio Agung Purnomo",
    author_email="laraflask@ryucode.com",
    description="Laraflask ecosystem init root.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/riodevnet/laraflask",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "MarkupSafe",
        "python-dotenv",
        "click"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
