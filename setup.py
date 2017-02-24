#!/usr/bin/env python
import glob
import subprocess
from setuptools import setup, find_packages
from os.path import join, abspath, dirname
import pip

# Fetch version from git tags.
#version = subprocess.Popen(["git", "describe", "--abbrev=0"],stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].rstrip()
#version = version.decode("utf-8")

requirements_txt = join(abspath(dirname(__file__)), 'requirements.txt')
# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
requirements = [l.strip() for l in open(requirements_txt) if l and not l.startswith('#')]


version = '0.1.1'


setup(
    name='clarity_scripts',
    version=version,
    packages=find_packages(exclude=('tests',)),
    url='https://github.com/EdinburghGenomics/clarity_scripts',
    license='MIT',
    description='Clarity EPPs used in Edinburgh Genomics',
    long_description='Set of scripts used at Edinburgh Genomics to automate steps of in Clarity LIMS',
    install_requires=requirements,  # actual module requirements
    scripts=glob.glob("bin/*.py"),
    zip_safe=False,
    author='Timothee Cezard',
    author_email='timothee.cezard@ed.ac.uk'

)