from setuptools import setup, find_packages

setup(
    name="drfgen",
    version="0.1.3",
    author="Mohammadreza Taheri",
    author_email="mrtcode2@gmail.com",
    description="A CLI tool to bootstrap Django REST Framework projects quickly and easily.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tahericode/DRFgen.git",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "questionary>=2.0",
        "requests>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "drfgen=drfgen.cli:start_cli",  
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Code Generators",
    ],
    include_package_data=True,
)