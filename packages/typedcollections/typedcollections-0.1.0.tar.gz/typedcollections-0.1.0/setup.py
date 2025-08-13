from setuptools import setup, find_packages

setup(
    name="typedcollections",
    version="0.1.0",
    author="Dev Khurana",
    author_email="devkhurana2004@gmail.com",
    description="Typed list and related typed collection classes with validation and coercion",
    # long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/typedcollections",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
