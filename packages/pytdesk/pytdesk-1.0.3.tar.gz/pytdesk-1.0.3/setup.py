from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytdesk",  # Your package name
    version="1.0.3",
    author="Scott Murray",
    author_email="scottmurray2789@gmail.com",
    description="A lightweight, robust Python client for interacting with the TalentDesk API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scottmurray2789/pytdesk",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.4",
        "urllib3>=2.5.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
