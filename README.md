# libcrowds-analyst

[![Build Status](https://travis-ci.org/alexandermendes/libcrowds-analyst.svg?branch=master)](https://travis-ci.org/alexandermendes/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/libcrowds-analyst/badge.svg?branch=master)](https://coveralls.io/github/alexandermendes/libcrowds-analyst?branch=master)


A web application to help with real-time analysis and verification of LibCrowds results.

# How it works

When a webhook is received from your PyBossa server to indicate that a task has
been completed the LibCrowds Analyst server pulls in all task runs associated
with that task and compares them according to the rules set out for the
project collection (see below).



## Convert-a-Card

When a webhook is received from your PyBossa server to indicate that a task has been completed
the LibCrowds Analyst server analyses all task runs associated with that task, looking for a specified
match rate for each answer key (disregarding task runs where all answer fields have been left
blank). If a match is found the result associated with the task is updated to the matched answer
for each key. If all keys for all answers have been left blank the result will be set to the
empty string for each key.For tasks where a match cannot be found the result will be set to
"Unverified" and the application provides templates to check each of these unverified answers
and manually set the final result.


## Requirements

- [PyBossa](https://github.com/PyBossa/pybossa) >= 1.2.0.
- A running [Redis](https://github.com/antirez/redis) server.


## Installation

Install the required development packages:

```
sudo apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
```

Install pybossa-analyst to a virtual environment:

```
git clone https://github.com/alexandermendes/pybossa-analyst
cd pybossa-analyst
virtualenv env
source env/bin/activate
python setup.py install
```


## Configuration

Copy the template settings file and edit according to the comments contained within:

```
cp settings.py.tmpl settings.py
vim settings.py
```


## Deploying with nginx and uwsgi

For deployment using nginx, uwsgi and supervisor a number of template files are
provided in the [contrib](./contrib) folder.


## Testing

To run tests:

```
python setup.py test
```
