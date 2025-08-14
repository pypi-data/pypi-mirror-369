from setuptools import setup, find_packages

setup(
    name="rubion",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
    author="Until Loop",
    author_email="info.untilloop@gmail.com",
    description="Python library for Rubika Bot API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/untilloop/rubion",
)