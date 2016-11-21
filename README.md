# pybossa-analyst

[![Build Status](https://travis-ci.org/alexandermendes/pybossa-analyst.svg?branch=master)]
(https://travis-ci.org/alexandermendes/pybossa-analyst)
[![Coverage Status](https://coveralls.io/repos/github/alexandermendes/pybossa-analyst/badge.svg?branch=master)]
(https://coveralls.io/github/alexandermendes/pybossa-analyst?branch=master)


A web application to help with real-time analysis of PyBossa results.

When a webhook is recieved from your PyBossa server to indicate that a task has been completed the application
analyses all of the task runs associated with that task, by default looking for a 60% match rate accross all
answer keys (i.e. 2 out of 3, 5 out of 8, or 12 out of 20 people entered the same answer etc.). For tasks where
a match could not be found the application provides templates to check each answer submitted for a task and select
the correct one (if present).

The basic process for analysis is as follows:

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

Install pybossa-analyst:

```
git clone https://github.com/alexandermendes/pybossa-analyst
cd pybossa-analyst
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
rqworker pybossa_analyst
```


## Deploying with nginx and uwsgi

For deployment using nginx and uwsgi, the following template files are provided:

- [contrib/uwsgi/pybossa-analyst.ini.tmpl](contrib/uwsgi/pybossa-analyst.ini.tmpl)
- [contrib/nginx/pybossa-analyst](contrib/nginx/pybossa-analyst)
- [contrib/supervisor/pybossa-analyst.conf.tmpl](contrib/supervisor/pybossa-analyst.conf.tmpl)


## PyBossa Theme Integration

If the location of the server changes, the `pybossa_analyst_URL` variable
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
