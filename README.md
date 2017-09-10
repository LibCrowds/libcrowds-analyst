# libcrowds-analyst

[![Build Status](https://travis-ci.org/alexandermendes/libcrowds-analyst.svg?branch=master)](https://travis-ci.org/alexandermendes/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/libcrowds-analyst/badge.svg?branch=master)](https://coveralls.io/github/alexandermendes/libcrowds-analyst?branch=master)

A headless web application to help with real-time analysis of LibCrowds results.

Recieves webhooks from a PyBossa server and analyses task runs according to the
rules set out for that project (see [Analysis](README.md#Analysis)). The  task's
result is updated accordingly.

## Requirements

- [PyBossa](https://github.com/PyBossa/pybossa) >= 1.2.0.
- A running [Redis](https://github.com/antirez/redis) server.


## Build setup

```bash
# Install dev packages
sudo apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

# Install LibCrowds Analyst
virtualenv env
source env/bin/activate
python setup.py install

# Run
python run.py

# Test
python setup.py test
```

For deployment using nginx, uwsgi and supervisor some basic templates are
provided in the [contrib](./contrib) folder.

## Configuration

Make a local copy of the configuration file to change the default settings:

```bash
cp settings.py.tmpl settings.py
```

## Analysis

Following is the analysis procudure for each project.

### Convert-a-Card

**WEBHOOK ENDPOINT:** `/convert-a-card`

All task runs are compared looking a match rate of at least 70% for the answer
keys `oclc` and `shelfmark` (disregarding task runs where all answer fields
have been left blank).

If a match is found the result associated with the task is updated to the
matched answer for each key and `analysis_complete` will be set to `True`.

If all keys for all answers have been left blank the result will be set to the
empty string for each key and `analysis_complete` will be set to `True`.

For all other cases the result will be set to the empty string for each key
and `analysis_complete` will be set to `False`. These are the  results that will
have to be checked manually, after which `analysis_complete` should be set to
`True`.

#### Example result
```json
{
  "info": {
    "comments": "",
    "shelfmark": "15673.d.13",
    "oclc": "865706215",
    "analysis": "https://github.com/LibCrowds/libcrowds-analyst/releases/tag/v3.0.0",
    "analysis_complete": true,
    "check_required": false
  },
  "links ": [
    "<link rel='parent' title='project' href='https://backend.libcrowds.com/api/project/3'/>",
    "<link rel='parent' title='task' href='https://backend.libcrowds.com/api/task/2298'/>"
  ],
  "task_id": 2298,
  "created": "2016-06-14T17:45:06.171456",
  "last_version": true,
  "link":"<link rel='self' title='result' href='https://backend.libcrowds.com/api/result/49225'/>",
  "task_run_ids": [
    537,
    551,
    578
  ],
  "project_id": 3,
  "id": 49225
}
```
