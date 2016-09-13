from __future__ import unicode_literals, division, absolute_import
from builtins import *  # pylint: disable=unused-import, redefined-builtin

import json

from flexget.api import base_message
from flexget.api.core_endpoints.tasks import ObjectsContainer as OC
from flexget.manager import Manager
from mock import patch


class TestTaskAPI(object):
    config = """
        tasks:
          test:
            rss:
              url: http://test/rss
            mock:
              - title: entry 1
        """

    def test_list_tasks(self, api_client, schema_match):
        rsp = api_client.get('/tasks/')
        data = json.loads(rsp.get_data(as_text=True))

        # TODO Need to figure out how to do this
        # errors = schema_match(OC.tasks_list_object, data)
        # assert not errors
        assert data == [
            {
                'name': 'test',
                'config': {
                    'mock': [{'title': 'entry 1'}],
                    'rss': {
                        'url': u'http://test/rss',
                        'group_links': False,
                        'ascii': False,
                        'silent': False,
                        'all_entries': True
                    }
                },
            }
        ]

    @patch.object(Manager, 'save_config')
    def test_add_task(self, mocked_save_config, api_client, manager, schema_match):
        new_task = {
            'name': 'new_task',
            'config': {
                'mock': [{'title': 'entry 1'}],
                'rss': {'url': 'http://test/rss'}
            }
        }

        return_task = {
            'name': 'test',
            'config': {
                'mock': [{'title': 'entry 1'}],
                'rss': {
                    'url': u'http://test/rss',
                    'group_links': False,
                    'ascii': False,
                    'silent': False,
                    'all_entries': True
                }
            },
        }

        rsp = api_client.json_post('/tasks/', data=json.dumps(new_task))
        data = json.loads(rsp.get_data(as_text=True))

        errors = schema_match(OC.task_return_object, data)
        assert not errors

        assert rsp.status_code == 201
        assert mocked_save_config.called
        assert data == new_task
        assert manager.user_config['tasks']['new_task'] == new_task['config']
        assert manager.config['tasks']['new_task'] == return_task['config']

    def test_add_task_existing(self, api_client, schema_match):
        new_task = {
            'name': 'test',
            'config': {
                'mock': [{'title': 'entry 1'}]
            }
        }

        rsp = api_client.json_post('/tasks/', data=json.dumps(new_task))
        assert rsp.status_code == 409
        data = json.loads(rsp.get_data(as_text=True))

        errors = schema_match(base_message, data)
        assert not errors

    def test_get_task(self, api_client, schema_match):
        rsp = api_client.get('/tasks/test/')
        data = json.loads(rsp.get_data(as_text=True))
        errors = schema_match(OC.task_return_object, data)
        assert not errors
        assert data == {
            'name': 'test',
            'config': {
                'mock': [{'title': 'entry 1'}],
                'rss': {
                    'url': u'http://test/rss',
                    'group_links': False,
                    'ascii': False,
                    'silent': False,
                    'all_entries': True
                }
            },
        }

    @patch.object(Manager, 'save_config')
    def test_update_task(self, mocked_save_config, api_client, manager, schema_match):
        updated_task = {
            'name': 'test',
            'config': {
                'mock': [{'title': 'entry 1'}],
                'rss': {'url': 'http://newurl/rss'}
            }
        }

        rsp = api_client.json_put('/tasks/test/', data=json.dumps(updated_task))

        assert rsp.status_code == 200
        data = json.loads(rsp.get_data(as_text=True))
        errors = schema_match(OC.task_return_object, data)
        assert not errors
        assert mocked_save_config.called
        assert data == updated_task
        assert manager.user_config['tasks']['test'] == updated_task['config']
        assert manager.config['tasks']['test'] == updated_task['config']

    @patch.object(Manager, 'save_config')
    def test_rename_task(self, mocked_save_config, api_client, manager, schema_match):
        updated_task = {
            'name': 'new_test',
            'config': {
                'mock': [{'title': 'entry 1'}],
                'rss': {'url': 'http://newurl/rss'}
            }
        }

        rsp = api_client.json_put('/tasks/test/', data=json.dumps(updated_task))

        assert rsp.status_code == 201
        data = json.loads(rsp.get_data(as_text=True))
        errors = schema_match(OC.task_return_object, data)
        assert not errors
        assert mocked_save_config.called
        assert data == updated_task
        assert 'test' not in manager.user_config['tasks']
        assert 'test' not in manager.config['tasks']
        assert manager.user_config['tasks']['new_test'] == updated_task['config']
        assert manager.config['tasks']['new_test'] == updated_task['config']

    @patch.object(Manager, 'save_config')
    def test_delete_task(self, mocked_save_config, api_client, manager, schema_match):
        rsp = api_client.delete('/tasks/test/')

        assert rsp.status_code == 200
        data = json.loads(rsp.get_data(as_text=True))
        errors = schema_match(base_message, data)
        assert not errors
        assert mocked_save_config.called
        assert 'test' not in manager.user_config['tasks']
        assert 'test' not in manager.config['tasks']
