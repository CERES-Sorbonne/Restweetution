from setuptools import setup, find_packages

INSTALL_REQUIRES = []

with open('requirements.txt', 'r') as f:
    for line in f.readlines():
        INSTALL_REQUIRES.append(line.strip())

setup(
    name="restweetution",
    version="0.0.1",
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES
)