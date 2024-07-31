from setuptools import setup, find_packages

setup(
    name="codable",
    version="0.1.1",
    author="Isaac Harrison Gutekunst",
    author_email="isaac@dancingvoid.com",
    description="A Python module for encoding and decoding objects using customizable serialization.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/igutekunst/python-codable",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Base dependencies
    ],
    extras_require={
        "django": ["Django>=3.0"],
        "json": [],
        "xml": ["lxml"],
        "all": ["Django>=3.0", "lxml"]
    },
)