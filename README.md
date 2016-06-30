# libcrowds-analyst

[![Build Status](https://travis-ci.org/LibCrowds/libcrowds-analyst.svg?branch=master)]
(https://travis-ci.org/LibCrowds/libcrowds-analyst)
[![Coverage Status](https://coveralls.io/repos/github/LibCrowds/libcrowds-analyst/badge.svg?branch=master)]
(https://coveralls.io/github/LibCrowds/libcrowds-analyst?branch=master)


A web application to help with real-time analysis of LibCrowds results.

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
virtualenv env
source env/bin/activate
pip install -r requirements.txt
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

- A function in [libcrowds_analyst/analysis.py](analysis.py) called **category_\<category_id>**
- A template in [libcrowds_analyst/templates](templates) called **category_\<category_id>.html**
