#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = 'PyPokerEngine',
    version = '0.0.1',
    description = 'Poker engine for poker AI development in Python ',
    license = 'MIT',
    author = 'ishikota',
    author_email = 'ishikota086@gmail.com',
    url = 'https://github.com/ishikota/PyPokerEngine.git',
    keywords = 'python poker ai',
    packages = ['pypoker2',
                'pypoker2.engine',
                'pypoker2.interface',
                'pypoker2.players',
                'pypoker2.players.sample'],
    install_requires = []
    )

