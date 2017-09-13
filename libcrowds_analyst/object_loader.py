# -*- coding: utf8 -*-
"""Object loader module for libcrowds-analyst."""


def load(func, **kwargs):
    """Load all domain objects.

    Mainly used for results, which enki doesn't handle.
    """
    query = kwargs or {}
    query['limit'] = 100
    items = func(**query)
    last_fetched = items
    while _not_exhausted(last_fetched, query):
        query['last_id'] = last_fetched[-1].id
        last_fetched = func(**query)
        items += last_fetched
    return items


def _not_exhausted(last_fetched, query):
    return len(last_fetched) != 0 and len(last_fetched) == query['limit']
