from setuptools import setup, find_packages

setup(name='race-results',
      version='0.1',
      description='A collection of utilities for processing race results',
      url='https://github.com/bnorthan/raceresults/',
      author='Brian Northan',
      author_email='bnorthan@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['python-Levenshtein', 'tabulate'],
      zip_safe=False)
