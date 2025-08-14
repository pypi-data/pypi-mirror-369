from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.4.4'
DESCRIPTION = 'amirhoshein library test'

# Setting up
setup(
    name="amirhoshein",
    version=VERSION,
    author="amir_hoshein",
    author_email="a.gaffarzadeh.1387.2@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests','user_agent'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)