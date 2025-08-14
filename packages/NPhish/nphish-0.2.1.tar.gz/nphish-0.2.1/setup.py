from setuptools import setup
import os

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
readme_loc = os.path.join(location, 'README.md')

long_description = open(readme_loc).read()
setup(name="NPhish",
version="0.2.1",
description="Ultimate phishing tool in python. Includes popular websites like facebook, twitter, instagram, github, reddit, gmail and many others.",
long_description=long_description,
long_description_content_type='text/markdown',
author="CodingSangh",
py_modules=[],
url="https://github.com/CodingSangh/NPhish",
scripts=["NPhish"],
install_requires= ['colourfulprint==1.5', 'colorama==0.4.5', 'requests==2.28.1'],
classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
], )
