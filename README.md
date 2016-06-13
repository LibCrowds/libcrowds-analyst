# libcrowds-analyst

[![Build Status](https://travis-ci.org/LibCrowds/libcrowds-analyst.svg?branch=master)]
(https://travis-ci.org/LibCrowds/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/LibCrowds/libcrowds-analyst/badge.svg?branch=master)]
(https://coveralls.io/github/LibCrowds/libcrowds-analyst?branch=master)


A web application to help with real-time analysis of LibCrowds results.

## Requirements

- [PyBossa](https://github.com/PyBossa/pybossa) >= 1.2.0.
- A running [Redis](https://github.com/antirez/redis) server.


## Installing, configuring and running

Run the following commands:

```
python setup.py install          # Install
cp settings.py.tmpl settings.py  # Copy (then edit) the settings
python run.py                    # Run the server
rqworker libcrowds_analyst       # Run a background worker
```


## Usage

All webhook payloads should be directed to the root url of this server. If an
analyser has been set up for the related category, results will be analysed
and updated automatically.

### Endpoints

- To process any unanalysed results visit:

```http
GET /<project_short_name>
```

- To directly edit a result visit:


```http
GET /<project_short_name>/<result_id>/edit
```

- To trigger reanalysis for all of a project's results visit:

```http
GET /<project_short_name>/reanalyse
```


## Creating a new analyser

To create an analyser for a new category you need to create:

- A function in [analysis.py](analysis.py) called **category_\<category_id>**
- A template in [templates](templates) called **category_\<category_id>.html**
