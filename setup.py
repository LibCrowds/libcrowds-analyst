import re
from setuptools import setup

requirements = [
    "Flask>=0.10.1, <0.10.2",
    "Flask-Z3950>=0.3.1, <1.0",
    "rq>=0.6.0, <1.0",
    "Flask-WTF>=0.9.5, <1.0",
    "requests>=2.0.0, <3.0",
    "enki>=1.1.0, <2.0"
]

setup_requirements = [
    "pytest-runner>=2.9, <3.0",
]

test_requirements = [
    "pytest>=3.0, <4.0",
    "pytest-cov>=2.3.1, <3.0",
    "pytest-mock>=1.0, <2.0"
]

version = re.search('^__version__\s*=\s*"(.*)"',
                    open('pybossa_analyst/__init__.py').read(),
                    re.M).group(1)

setup(
    name="pybossa-analyst",
    version=version,
    author="Alexander Mendes",
    author_email="alexanderhmendes@gmail.com",
    description="A web application to help analyse of PyBossa results.",
    license="BSD",
    url="https://github.com/alexandermendes/pybossa-analyst",
    zip_safe=False,
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    test_suite="test",
)
