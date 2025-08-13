from setuptools import setup, find_packages

setup(
    name="ATmulti_file_handler",
    version="1.0.0",
    author="Avi Twil",
    author_email="avitwil@gmail.com",
    description="A flexible file handler supporting text, JSON, YAML, CSV, XML, dill, and binary formats.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ATmulti_file_handler",  # תעדכן
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "pyyaml>=6.0",
        "dill>=0.3.7"
    ]
)
