# -*- coding: utf8 -*-
"""Test the object loader module for libcrowds-analyst."""

from libcrowds_analyst import object_loader


class TestObjectLoader(object):

    def test_correct_objects_are_loaded(self, result):
        """Test that objects are loaded."""
        def mock_func():
            return [result]
        object_list = object_loader.load(mock_func)
        assert object_list == [result]

    def test_all_objects_are_loaded(self, result):
        """Test that all objects are loaded."""
        def mock_func():
            return [result]*100
        object_list = object_loader.load(mock_func)
        assert len(object_list) == 200
