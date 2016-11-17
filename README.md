# libcrowds-analyst

[![Build Status](https://travis-ci.org/LibCrowds/libcrowds-analyst.svg?branch=master)]
(https://travis-ci.org/LibCrowds/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/LibCrowds/libcrowds-analyst/badge.svg?branch=master)]
(https://coveralls.io/github/LibCrowds/libcrowds-analyst?branch=master)


A web application to help with real-time analysis of LibCrowds results.

By default, we're looking for a 60% match rate for all contributions to a task. When a task is completed
and the webhook payload directed to this server the following steps are followed:

- Check that the info fields of each task run match n percent of the time or above, disregarding task runs
where all of the info fields are blank.
- For tasks where we have a sufficent number of matches the result will be set to a dictionary containing
the task run info keys and the matched values.
- For tasks where all info fields of all task runs are empty the result will be set to a dictionary containing
the task run info keys and empty values.
- For all other tasks the result will be set to the string 'Unanalysed' so that the different answers can be checked
manually later.


## Requirements

- [PyBossa](https://github.com/PyBossa/pybossa) >= 1.2.0.
- A running [Redis](https://github.com/antirez/redis) server.


## Installation

Install the required development packages:

```
sudo apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
```

Install libcrowds-analyst:

```
git clone https://github.com/LibCrowds/libcrowds-analyst
cd libcrowds-analyst
python setup.py install
```


## Configuration

Copy the template settings file:

```
cp settings.py.tmpl settings.py
```

Now edit this file according to the comments contained within.


## Running

Run the server:

```
python run.py
```


Run a background worker:

```
rqworker libcrowds_analyst
```


## Deploying with nginx and uwsgi

For deployment using nginx and uwsgi, the following template files are provided:

- [contrib/uwsgi/libcrowds-analyst.ini.tmpl](contrib/uwsgi/libcrowds-analyst.ini.tmpl)
- [contrib/nginx/libcrowds-analyst](contrib/nginx/libcrowds-analyst)
- [contrib/supervisor/libcrowds-analyst.conf.tmpl](contrib/supervisor/libcrowds-analyst.conf.tmpl)


## LibCrowds Theme Integration

If the location of the server changes, the `LIBCROWDS_ANALYST_URL` variable
should be updated in the main PyBossa configuration.


### Endpoints

- Process the next unanalysed result:

```http
GET /<project_short_name>
```

- Process a specific result:

```http
GET /<project_short_name>/<result_id>
```

- Trigger reanalysis for all of a project's results:

```http
GET /<project_short_name>/reanalyse
```

- Download the original input (e.g. the images) associated with a list of tasks:

```http
GET /<project_short_name>/download
```
