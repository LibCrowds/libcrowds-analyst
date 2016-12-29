# -*- coding: utf8 -*-

import enki
from pytest_mock import mocker
from pybossa_analyst.client import PyBossaClient


class TestClient(object):
    """Test client module."""

    def test_imported_task_run_df(self, task, project, mocker, app):
        """Test task run dataframe is created using the correct data."""
        mock_client = mocker.patch('pybossa_analyst.client.enki.pbclient')
        mock_enki = mocker.patch('pybossa_analyst.client.enki.Enki')
        mock_enki = enki.Enki(endpoint='endpoint', api_key='api_key',
                              project_short_name=project.short_name)
        client = PyBossaClient(app)
        expected_df = mock_enki.task_runs_df[task.id]
        df = client.get_task_run_dataframe(project.id, task.id)

        mock_client.find_project.assert_called_with(all=1, limit=1,
                                                    id=project.id)
        mock_enki.get_tasks.assert_called_with(task_id=task.id)
        mock_enki.get_task_runs.assert_called
        assert df == expected_df
