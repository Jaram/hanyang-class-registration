#-*- coding:utf-8 -*-
from distutils.core import setup

setup(
    name = 'hanyang_registration',
    packages = ['hanyang_registration'],
    version = '1.1.1',
    description = 'Hanyang Class Registration for python',
    license = 'The MIT License',
    author = 'Jin-Soo Han, Jaram',
    author_email = 'jinsu0411@gmail.com',
    url = 'https://github.com/Jaram/Hanyang-Class-Registration',
    keywords = ['hanyang', 'registration'],
    classifiers = [],
    long_description=open('README.rst').read(),
    install_requires=[
       'rsa',
       'requests'
    ]
)