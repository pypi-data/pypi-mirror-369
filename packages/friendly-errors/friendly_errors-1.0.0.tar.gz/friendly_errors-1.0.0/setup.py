from setuptools import setup, find_packages

setup(
    name="friendly-errors",
    version="1.0.0",
    author="Maurya Suryakant",
    author_email="mauryasuryakant99@gmail.com",
    description="A Python utility for clean, colorful, and helpful error messages with suggestions.",
    long_description=open("README.md", "r", encoding="utf-8").read() if False else "",
    long_description_content_type="text/markdown",
    url="https://github.com/white-darkness/friendly-errors-python",
    packages=find_packages(),
    install_requires=["colorama>=0.4.6"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
