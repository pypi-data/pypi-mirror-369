from setuptools import setup, find_packages

setup(
    name="memhook",           # <-- new PyPI name
    version="0.1.0",
    description="Modern Python memory reading/writing library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="YourName",
    packages=find_packages(),
    install_requires=["psutil"],
    python_requires='>=3.8',
)
