# pybossa-analyst

[![Build Status](https://travis-ci.org/alexandermendes/pybossa-analyst.svg?branch=master)]
(https://travis-ci.org/alexandermendes/pybossa-analyst)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/pybossa-analyst/badge.svg?branch=master)]
(https://coveralls.io/github/alexandermendes/pybossa-analyst?branch=master)


A web application to help with real-time analysis and verification of PyBossa results.

When a webhook is recieved from your PyBossa server to indicate that a task has been completed the application
analyses all task runs associated with that task, by default looking for a specified match rate for each answer
key. If a match is found the result associated with the task is updated automatically. For tasks where a match
cannot be found the application provides templates to check each answer and set the final result.


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
