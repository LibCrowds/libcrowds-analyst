# -*- coding: utf8 -*-
"""Test the object loader module for libcrowds-analyst."""

from libcrowds_analyst import object_loader


class TestObjectLoader(object):

    def test_correct_objects_are_loaded(self, result):
        """Test that objects are loaded."""
        def mock_func(**kwargs):
            return [result]
        object_list = object_loader.load(mock_func)
        assert object_list == [result]

    def test_all_objects_are_loaded(self, result):
        """Test that all objects are loaded."""
        long_list = [result]*100

        def mock_func(**kwargs):
            return long_list
        object_list = object_loader.load(mock_func)
        assert len(object_list) == 200
