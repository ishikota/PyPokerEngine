from setuptools import setup, find_packages

setup(
    name = 'PyPokerEngine',
    version = '0.0.1',
    author = 'ishikota',
    author_email = 'ishikota086@gmail.com',
    description = 'Poker engine for poker AI development in Python ',
    license = 'MIT',
    keywords = 'python poker emgine ai',
    url = 'https://github.com/ishikota/PyPokerEngine',
    packages = [pkg for pkg in find_packages() if pkg != "tests"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    )

