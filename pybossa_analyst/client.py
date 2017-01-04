# -*- coding: utf8 -*-
"""API client module for pybossa-analyst."""

import pbclient


def _load(func, **query):
    query['limit'] = 100
    items = func(**query)
    last_fetched = items
    while _not_exhausted(last_fetched, query):
        query['last_id'] = last_fetched[-1].id
        last_fetched = func(**query)
        items += last_fetched
    return items

def _not_exhausted(last_fetched, query):
    return (len(last_fetched) != 0 and len(last_fetched) == query['limit'])

def get_all_results(**kwargs):
    """Return all results."""
    return _load(pbclient.find_results, **kwargs)

def get_all_projects(**kwargs):
    """Return all projects."""
    return _load(pbclient.find_project, **kwargs)
