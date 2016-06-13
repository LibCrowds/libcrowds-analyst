# libcrowds-analyst

[![Build Status](https://travis-ci.org/LibCrowds/libcrowds-analyst.svg?branch=master)]
(https://travis-ci.org/LibCrowds/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/LibCrowds/libcrowds-analyst/badge.svg?branch=master)]
(https://coveralls.io/github/LibCrowds/libcrowds-analyst?branch=master)


A web application to help with analysis of LibCrowds results, inspired by the
PyBossa [webhooks](https://github.com/PyBossa/webhooks) module.

## Requirements

- PyBossa >= 1.2.0.
- A running Redis server.


## Installing, configuring and running

Run the following commands:

```
python setup.py install          # Install
cp settings.py.tmpl settings.py  # Copy (then edit) the settings
python run.py                    # Run the server
rqworker mywebhooks              # Run background worker
```


## Usage

All webhook payloads should be directed to the root url of this server. If an
analyser has been set up for the related category, the result will be analysed
and updated.

### Endpoints

- To process unanalysed results visit `/<project_short_name>`.

- To directly edit a result visit `/<project_short_name>/<result_id>`.

- To trigger reanalysis for all of a project's results visit `/<project_short_name>/reanalyse`.


## Analysing a new category

To develop an analyser for a new category you need to create a function in
[analysis.py](analysis.py) called **category_<category_id>** and a template
in [templates](templates) called **category_<category_id>.html**.
