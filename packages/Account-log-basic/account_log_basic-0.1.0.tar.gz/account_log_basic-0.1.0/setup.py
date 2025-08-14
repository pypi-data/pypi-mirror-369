
from setuptools import setup, find_packages

setup(
    name="Account_log_basic",  # Your package name (must be unique on PyPI)
    version="0.1.0",           # Start with 0.1.0
    packages=find_packages(),  # Finds your __init__.py automatically
    install_requires=[],       # List any dependencies here (empty if none)
    description="A basic account login and creation module in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/Account_log_basic",  # Optional GitHub URL
)
