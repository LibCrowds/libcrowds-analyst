# -*- coding: utf8 -*-


class TestAuth(object):
    """Test auth module."""

    def test_basic_auth_not_required_for_index(self, test_client):
        """Test that basic auth is not required for index."""
        get_res = test_client.get('/')
        post_res = test_client.post('/')
        assert get_res.status_code == 200
        assert post_res.status_code == 200

    def test_basic_auth_required_for_all_other_pages(self, test_client, app):
        """Test that basic auth is required for all other pages."""
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'analyse.index':
                url = str(rule)
                get_res = test_client.get(url)
                post_res = test_client.get(url)
                assert get_res.status_code == 401
                assert post_res.status_code == 401

    def test_basic_auth_credentials_accepted(self, test_client, auth_headers):
        """Test that authorisation credentials are accepted."""
        res = test_client.get("/short_name", headers=auth_headers)
        assert res.status_code == 301
