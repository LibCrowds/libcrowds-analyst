# -*- coding: utf8 -*-
"""Test the object loader module for libcrowds-analyst."""

from libcrowds_analyst import object_loader


class TestObjectLoader(object):

    def test_correct_objects_are_loaded(self, result):
        """Test that objects are loaded."""
        func = lambda **x: [result]
        object_list = object_loader.load(func)
        assert object_list == [result]

    def test_all_objects_are_loaded(self, result):
        """Test that all objects are loaded."""
        long_list = [result]*100
        func = lambda **x: long_list
        object_list = object_loader.load(func)
        assert len(object_list) == 200
