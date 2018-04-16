import mock
import unittest
import json
import requests
from fixtures import *
from itsi_event_management_sdk import Event, EventMeta, EventGroup, Client


class TestEventMeta(unittest.TestCase):
    
    @mock.patch('itsi_event_management_sdk.Client.request')
    def test_001_test_event_meta(self, client_request):
        return_value = EVENT_META
        client_request.return_value = return_value
        a = EventMeta('admin', 'qwqwqw',
                      'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        client_request.assert_called_with('GET', 'event_management_interface/notable_event_configuration/all_info')
        self.assertEqual(a.get_all_statuses(), return_value.get('statuses')) 
        self.assertEqual(a.get_all_severities(), return_value.get('severities')) 
        self.assertEqual(a.get_all_owners(), return_value.get('owners')) 


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.get_from_index_return_value = GET_FROM_INDEX
    
    @mock.patch('itsi_event_management_sdk.Client.request')
    def test_001_test_get_from_index(self, request):
        
        request.return_value = self.get_from_index_return_value
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a._get_from_index(['e28f6a23-e447-11e7-bf0b-acbc32b4d98f']),
                self.get_from_index_return_value)
        request.assert_called_with('GET', 'event_management_interface/notable_event',
                params={'ids': '["e28f6a23-e447-11e7-bf0b-acbc32b4d98f"]'})


    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_002_test_get_severity(self, request):
        request.return_value = self.get_from_index_return_value
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.get_severity(
                event_ids=[
                    'e28f6a23-e447-11e7-bf0b-acbc32b4d98f'],
                latest_time='-1s',
                earliest_time= '-1d'),
            [('e28f6a23-e447-11e7-bf0b-acbc32b4d98f', u'low')]
        )
        request.assert_called_with('GET', 'event_management_interface/notable_event',
                params={'earliest_time': '-1d', 'latest_time': '-1s',
                    'ids': '["e28f6a23-e447-11e7-bf0b-acbc32b4d98f"]'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_003_test_get_status(self, request):
        request.return_value = self.get_from_index_return_value
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.get_status(
                event_ids=[
                    'e28f6a23-e447-11e7-bf0b-acbc32b4d98f'],
                latest_time='-1s',
                earliest_time= '-1d'),
            [('e28f6a23-e447-11e7-bf0b-acbc32b4d98f', u'new')]
        )
        request.assert_called_with('GET', 'event_management_interface/notable_event',
                params={'earliest_time': '-1d', 'latest_time': '-1s',
                    'ids': '["e28f6a23-e447-11e7-bf0b-acbc32b4d98f"]'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_004_test_get_owner(self, request):
        request.return_value = self.get_from_index_return_value
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.get_owner(
                event_ids=[
                    'e28f6a23-e447-11e7-bf0b-acbc32b4d98f'],
                latest_time='-1s',
                earliest_time= '-1d'),
            [('e28f6a23-e447-11e7-bf0b-acbc32b4d98f', u'admin')]
        )
        request.assert_called_with('GET', 'event_management_interface/notable_event',
                params={'earliest_time': '-1d', 'latest_time': '-1s',
                    'ids': '["e28f6a23-e447-11e7-bf0b-acbc32b4d98f"]'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_005_test_update(self, request):
        request.return_value = UPDATE_BLOB
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        blob = [
          {
            'event_ids': [
              'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
              '031f06c0-e453-11e7-b054-acbc32b4d98f'
            ],
            'severity': 'high',
            'status': 'closed',
          }
        ]
        self.assertEqual(a.update(blob), UPDATE_BLOB)
        request.assert_called_with('PUT',
                                   'event_management_interface/notable_event',
        data=[{'status': 'closed',
               'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
               'severity': 'high'}, {'status': 'closed',
               'event_id': '031f06c0-e453-11e7-b054-acbc32b4d98f',
               'severity': 'high'}], params={})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_006_test_update_severity(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.update_severity(['e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                           '031f06c0-e453-11e7-b054-acbc32b4d98f'],'low')
        request.assert_called_with('PUT', 'event_management_interface/notable_event',
                                   data=[{'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                                          'severity': 'low'},
                                          {'event_id': '031f06c0-e453-11e7-b054-acbc32b4d98f',
                                           'severity': 'low'}],
                                    params={})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_007_test_update_owner(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.update_owner(['e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                        '031f06c0-e453-11e7-b054-acbc32b4d98f'],'admin')
        request.assert_called_with('PUT', 'event_management_interface/notable_event',
                                   data=[{'owner': 'admin',
                                          'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f'},
                                         {'owner': 'admin',
                                          'event_id': '031f06c0-e453-11e7-b054-acbc32b4d98f'}],
                                   params={})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_008_test_create_tag(self, request):
        request.return_value = CREATE_TAG
        a = Event('admin','qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.create_tag('e28f6a23-e447-11e7-bf0b-acbc32b4d98f', 'test'),
                         {'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                          'tag_name': 'test',
                          'tag_id': u'5a4c14fb9693fb9dbf20acc1'})
        request.assert_called_with('POST', 'event_management_interface/notable_event_tag',
                                   data={'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                                         'tag_name': 'test'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_009_test_update_tag(self, request):
        a = Event('admin','qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.update_tag('e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                     '5a394f449693fbcbf741b3e6', 'test')
        request.assert_called_with('PUT', 'event_management_interface/notable_event_tag',
                                   data={'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                                         '_key': '5a394f449693fbcbf741b3e6',
                                         'tag_name': 'test'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_010_test_get_all_tags(self, request):
        request.return_value = GET_ALL_TAGS
        a = Event('admin','qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.get_all_tags('e28f6a23-e447-11e7-bf0b-acbc32b4d98f'),
                         ['test'])
        request.assert_called_with('GET',
                                   'event_management_interface/notable_event_tag/e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                                    params={'is_event_id': True})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_011_test_get_tag(self, request):
        a = Event('admin','qwqwqw',
                 'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.get_tag('5a394f449693fbcbf741b3e6')
        request.assert_called_with('GET',
                'event_management_interface/notable_event_tag/5a394f449693fbcbf741b3e6')

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_012_test_delete_tag(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.delete_tag('5a394f449693fbcbf741b3e6')
        request.assert_called_with('DELETE',
                'event_management_interface/notable_event_tag/5a394f449693fbcbf741b3e6')

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_013_delete_all_tags(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.delete_all_tags('e28f6a23-e447-11e7-bf0b-acbc32b4d98f')
        request.assert_called_with('DELETE',
                'event_management_interface/notable_event_tag/e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                params={'is_event_id': True})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_014_test_create_comment(self, request):
        request.return_value = CREATE_COMMENT
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.create_comment('e28f6a23-e447-11e7-bf0b-acbc32b4d98f','test'),
                        {'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                         'comment': 'test',
                         'comment_id': u'5a4c1b589693fb9dbf20acc2'})
        request.assert_called_with('POST',
                                   'event_management_interface/notable_event_comment',
                                   data={'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                                         'comment': 'test'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_get_comment(self, request):
        request.return_value = GET_COMMENT
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.get_comment('5a4c1b589693fb9dbf20acc2'),'test')
        request.assert_called_with('GET',
                'event_management_interface/notable_event_comment/5a4c1b589693fb9dbf20acc2')

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_get_all_comments(self, request):
        request.return_value = GET_ALL_COMMENTS
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.get_all_comments('e28f6a23-e447-11e7-bf0b-acbc32b4d98f'),
                         [u'test1', u'test'])
        request.assert_called_with('GET', 
                'event_management_interface/notable_event_comment/e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                params={'is_event_id': True})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_delete_comment(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.delete_comment('5a3951289693fbcbf741b3e8')
        request.assert_called_with('DELETE',
                'event_management_interface/notable_event_comment/5a3951289693fbcbf741b3e8')

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_delete_all_comments(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.delete_all_comments('e28f6a23-e447-11e7-bf0b-acbc32b4d98f')
        request.assert_called_with('DELETE', 
                'event_management_interface/notable_event_comment/e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                params={'is_event_id': True})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_update_comment(self, request):
        a = Event('admin','qwqwqw','https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.update_comment('e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                         '5a3951ae9693fbcbf741b3ea','test2')
        request.assert_called_with('PUT',
                                   'event_management_interface/notable_event_comment',
                                   data={'event_id': 'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                                         '_key': '5a3951ae9693fbcbf741b3ea',
                                         'comment': 'test2'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_update_ticket_info(self, request):
        request.return_value = UPDATE_TICKET_INFO
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        self.assertEqual(a.update_ticket_info(['e28f6a23-e447-11e7-bf0b-acbc32b4d98f'],
                              'test', "124", "http://google.com/"),
                         {'failed': [], 'success': ['124']})
        request.assert_called_with('PUT',
                'event_management_interface/ticketing/e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
                data={'ticket_url': 'http://google.com/',
                      'ticket_system': 'test',
                      'ticket_id': '124'})

    @mock.patch('itsi_event_management_sdk.Event.request')
    def test_015_test_delete_ticket_info(self, request):
        a = Event('admin', 'qwqwqw',
                  'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.delete_ticket_info(['e28f6a23-e447-11e7-bf0b-acbc32b4d98f'],'test',"124")
        request.assert_called_with('DELETE', 
                'event_management_interface/ticketing/e28f6a23-e447-11e7-bf0b-acbc32b4d98f/test/124')


class TestEventGroup(unittest.TestCase):
    
    @mock.patch('itsi_event_management_sdk.EventGroup.request')
    def test_001_test_add_drilldown(self, request):
        request.return_value = GET_GROUP
        a = EventGroup('admin','qwqwqw','https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.add_drilldown('b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                        {'name': "DrilldownName",'link': "http://drill.down"})
        request.assert_called_with('PUT',
                                   'event_management_interface/notable_event_group',
                                   data={
                                        'event_id': 'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                                        '_key': 'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                                        'drilldown': [
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.dow',
                                            u'name': u'DrillownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            u'link': u'http://drill.down',
                                            u'name': u'DrilldownName'
                                        },
                                        {
                                            'link': 'http://drill.down',
                                            'name': 'DrilldownName'
                                        }
                                      ]
                                 })

    @mock.patch('itsi_event_management_sdk.EventGroup.request')
    def test_002_test_update_drilldown(self, request):
        request.return_value = GET_GROUP
        a = EventGroup('admin', 'qwqwqw',
                'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.update_drilldown('b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',{'name': "DrillownName",'link': "http://drill.dow"})
        request.assert_called_with('PUT',
                                   'event_management_interface/notable_event_group',
                                   data={
                                      'event_id': 'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                                      '_key': 'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                                      'drilldown': [
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': 'http://drill.dow',
                                          u'name': 'DrillownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          'link': 'http://drill.down',
                                          'name': 'DrilldownName'
                                        }
                                      ]
                                   })

    @mock.patch('itsi_event_management_sdk.EventGroup.request')
    def test_003_test_delete_drilldown(self, request):
        request.return_value = GET_GROUP
        a = EventGroup('admin', 'qwqwqw',
                       'https://localhost:8089/servicesNS/nobody/SA-ITOA')
        a.delete_drilldown('b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                           {'name': "DrilldownName",
                           'link': "http://drill.dow"})
        request.assert_called_with('PUT',
                                   'event_management_interface/notable_event_group',
                                   data={
                                      'event_id': 'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                                      '_key': 'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
                                      'drilldown': [
                                        {
                                          u'link': 'http://drill.dow',
                                          u'name': 'DrillownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          u'link': u'http://drill.down',
                                          u'name': u'DrilldownName'
                                        },
                                        {
                                          'link': 'http://drill.down',
                                          'name': 'DrilldownName'
                                        }
                                      ]
                                   })

if __name__ == '__main__':
    unittest.main()
