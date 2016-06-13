# -*- coding: utf8 -*-

import pytest


class TestView(object):

    def test_basic_auth_required(self, test_client, app):
        res = test_client.get('/')
        assert res.status_code == 401

    def test_auth_credentials_accepted(self, test_client, app, auth_headers):
        res = test_client.get("/", headers=auth_headers)
        assert res.status_code == 200
