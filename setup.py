#!/usr/bin/env python
import glob
from setuptools import setup
from os.path import join, abspath, dirname

requirements_txt = join(abspath(dirname(__file__)), 'requirements.txt')
requirements = [l.strip() for l in open(requirements_txt) if l and not l.startswith('#')]

version = '0.12.3'


setup(
    name='clarity_scripts',
    version=version,
    packages=['EPPs'],
    package_data={'EPPs': ['etc/*']},
    url='https://github.com/EdinburghGenomics/clarity_scripts',
    license='MIT',
    description='Clarity EPPs used in Edinburgh Genomics',
    long_description='Set of scripts used at Edinburgh Genomics to automate steps of in Clarity LIMS',
    install_requires=requirements,  # actual module requirements
    scripts=glob.glob('scripts/*.py') + glob.glob('prodscripts/*.py'),
    zip_safe=False,
    author='Timothee Cezard',
    author_email='timothee.cezard@ed.ac.uk'

)
