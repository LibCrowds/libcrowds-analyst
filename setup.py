import re
from setuptools import setup

requirements = [
    "Flask>=0.10.1, <0.10.2",
    "Flask-Z3950>=0.3.1, <1.0",
    "rq>=0.6.0, <1.0",
    "Flask-WTF>=0.9.5, <1.0",
    "requests>=2.0.0, <3.0",
    "rq-scheduler>=0.7.0, <1.0",
    "enki"
]

setup_requirements = [
    "pytest-runner>-2.6.0, <3.0.0",
]

test_requirements = [
    "pytest>=2.8.0, <3.0",
    "pytest-cov>=2.2.0, <3.0",
    "pytest-mock>=0.11.0, <1.0"
]

# Remove once issue fixed - https://github.com/PyBossa/enki/issues/17
dependency_links = [
    'git+https://github.com/alexandermendes/enki.git'
    '@issue-retrieve-all-projects#egg=enki'
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
    dependency_links=dependency_links,
    test_suite="test",
)
