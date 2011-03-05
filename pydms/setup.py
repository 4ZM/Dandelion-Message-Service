import os
import re
from setuptools import setup

# Utility function to read the *.txt files used for some fields
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Utility to format the authors file to fit the author field
def get_authors(afile):
    return re.sub('[\r\n]', ', ', read(afile))

setup(
    name = "pydms",
    version='0.1',
    description='An implementation of the distributed, asyncronous, p2p message passing protocol Dandelion Message System (DMS)',
    author=get_authors('AUTHORS.txt'),
    maintainer_email='contact@dandelionmessaging.org',
    url='https://www.dandelionmessageing.org/pydms',
	  license='GPLv3',
    packages=['dandelion', 'dandelion.test'],
    keywords = "network p2p messaging",
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GPLv3",
    ],
)

