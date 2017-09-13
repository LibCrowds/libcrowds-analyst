# libcrowds-analyst

[![Build Status](https://travis-ci.org/libcrowds/libcrowds-analyst.svg?branch=master)](https://travis-ci.org/alexandermendes/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/libcrowds/libcrowds-analyst/badge.svg?branch=master)](https://coveralls.io/github/alexandermendes/libcrowds-analyst?branch=master)

A headless web application to help with real-time analysis of LibCrowds results.

Recieves webhooks from a PyBossa server and analyses task runs according to the
rules set out for that project (see [Analysis](README.md#Analysis)). The  task's
result is updated accordingly.

To facilitate reproducible research, since v3.0.0 the DOI of the version of
LibCrowds Analyst and the enpoint used for analysis are added to each result.

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

The important settings to maintain are:

```
# PyBossa API key for an admin user, used to update all results
API_KEY = ''

# URL of the PyBossa server
ENDPOINT = 'http://{your-pybossa-server}'

# DOI of the current LibCrowds Analyst version
DOI = ''
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

#### Example result info
```json
{
  "comments": "",
  "shelfmark": "15673.d.13",
  "oclc": "865706215",
  "doi": "10.5281/zenodo.888152",
  "analysis_complete": true
}
```

### In the Spotlight: Selections

**WEBHOOK ENDPOINT:** `/playbills/selections`

The annotations for all task runs are compared. Those with similar selection
rectangles are clustered and `analysis_complete` is set to `True`.

#### Example result info
```json
{
  "annotations": [],
  "doi": "10.5281/zenodo.888152",
  "analysis_complete": true
}
```
