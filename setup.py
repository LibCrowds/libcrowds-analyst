import re
from setuptools import setup

requirements = [
    "Flask>=0.10.1, <0.10.2",
    "rq>=0.6.0, <1.0",
    "Flask-WTF>=0.9.5, <1.0",
    "enki>=1.0.3, <=2.0"
]

setup_requirements = [
    "pytest-runner>-2.6.0, <3.0.0",
]

test_requirements = [
    "pytest>=2.8.0, <3.0",
    "pytest-cov>=2.2.0, <3.0",
    "pytest-mock>=0.11.0, <1.0"
]

version = re.search('^__version__\s*=\s*"(.*)"',
                    open('libcrowds_analyst/__init__.py').read(),
                    re.M).group(1)

setup(
    name="libcrowds-analyst",
    version=version,
    author="Alexander Mendes",
    author_email="alexanderhmendes@gmail.com",
    description="A web application to help analyse of LibCrowds results.",
    license="BSD",
    url="https://github.com/LibCrowds/libcrowds-analyst",
    zip_safe=False,
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    test_suite="test",
)
