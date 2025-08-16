from setuptools import setup, find_packages

with open("PYPI_README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fragment-api-py",
    version="1.1.0",
    author="S1qwy",
    author_email="amirhansuper75@gmail.com",
    description="Python client for Fragment API (fragment.com)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/S1qwy/fragment-api-py",
    packages=find_packages(include=['FragmentAPI', 'FragmentAPI.*']),
    package_dir={'': '.'},
    install_requires=[
        "requests>=2.25.1",
        "dataclasses>=0.6;python_version<'3.7'",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="fragment, telegram, ton, stars, premium, api",
    project_urls={
        "Bug Reports": "https://github.com/S1qwy/fragment-api-py/issues",
        "Source": "https://github.com/S1qwy/fragment-api-py",
    },
)