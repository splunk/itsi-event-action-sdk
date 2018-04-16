EVENT_META = {
        u'owners': [
            {
              u'default': False,
              u'value': u'user1',
              u'label': u'user1'
            },
            {
              u'default': True,
              u'value': u'unassigned',
              u'label': u'unassigned'
            },
            {
              u'default': False,
              u'value': u'foo',
              u'label': u'foo'
            },
            {
              u'default': False,
              u'value': u'superfoo',
              u'label': u'superfoo'
            },
            {
              u'default': False,
              u'value': u'non_itoa_user',
              u'label': u'non_itoa_user'
            },
            {
              u'default': False,
              u'value': u'analyst1',
              u'label': u'analyst1'
            },
            {
              u'default': False,
              u'value': u'admin',
              u'label': u'Administrator'
            }],
        u'email_formats': [
            {
              u'default': True,
              u'value': u'pdf',
              u'label': u'pdf'
            },
            {
              u'default': False,
              u'value': u'html',
              u'label': u'html'
            },
            {
              u'default': False,
              u'value': u'csv',
              u'label': u'csv'
            }],
      u'statuses': [
            {
              u'default': False,
              u'value': u'2',
              u'label': u'In progress'
            },
            {
              u'default': False,
              u'value': u'3',
              u'label': u'Pending'
            },
            {
              u'default': False,
              u'value': u'0',
              u'label': u'Unassigned'
            },
            {
              u'default': True,
              u'value': u'1',
              u'label': u'New'
            },
            {
              u'default': False,
              u'value': u'4',
              u'label': u'Resolved'
            },
            {
              u'default': False,
              u'value': u'5',
              u'label': u'Closed'
            }],
      u'severities': [
            {
              u'color': u'#99D18B',
              u'default': False,
              u'value': u'2',
              u'label': u'Normal'
            },
            {
              u'color': u'#FFE98C',
              u'default': False,
              u'value': u'3',
              u'label': u'Low'
            },
            {
              u'color': u'#AED3E5',
              u'default': True,
              u'value': u'1',
              u'label': u'Info'
            },
            {
              u'color': u'#B50101',
              u'default': False,
              u'value': u'6',
              u'label': u'Critical'
            },
            {
              u'color': u'#FCB64E',
              u'default': False,
              u'value': u'4',
              u'label': u'Medium'
            },
            {
              u'color': u'#F26A35',
              u'default': False,
              u'value': u'5',
              u'label': u'High'
            }
        ]
    }

GET_FROM_INDEX = [
     {
        u'orig_sourcetype': u'itsi_internal_log',
        u'object_type': u'notable_event_state',
        u'drilldown_uri': u'null',
        u'create_time': 1513704817.65209,
        u'owner': u'admin',
        u'rid': u'0',
        u'drilldown_search_latest_offset': u'null',
        u'search_type': u'basic',
        u'drilldown_search_search': u'null',
        u'event_identifier_hash':
        u'4e51c2edf96b4e9557ebafa5a05913102349ed25591013cac32902873c9bf5c3',
        u'severity': u'low',
        u'title':
        u'Error found in /Applications/Splunk/var/log/splunk/itsi_searches.log',
        u'drilldown_search_earliest_offset': u'null',
        u'source': u'Test Correlation Search - c09aeb1c-b271-4a5d-b76e-a7850c0c9e5a',
        u'serviceid': u'change_handler_test_service1234_key_12345',
        u'event_identifier_fields': u'source',
        u'_time': u'1513638305.000000',
        u'status': u'new',
        u'drilldown_title': u'null',
        u'orig_raw': u'2017-12-18 15:04:59,726 ERROR [itsi.command.set_severity] [set_severity_fields] [get_kpi] [56635] Service (serviceid=change_handler_test_service1234_key_12345) does not exist in kv store',
        u'description': u'Found error in source=/Applications/Splunk/var/log/splunk/itsi_searches.log and host=akompotis2mbp15',
        u'orig_sid': u'scheduler__admin__itsi__RMD5e1d07c484062dfa6_at_1513638300_317',
        u'drilldown_search_title': u'null',
        u'component': u'itsi.command.set_severity',
        u'is_use_event_time': u'0',
        u'orig_rid': u'0',
        u'host': u'akompotis2mbp15',
        u'sourcetype': u'stash',
        u'mod_time': 1513705110.63463,
        u'service_ids': u'624c440e-9702-483b-994e-eb8f90f2c8c1',
        u'_key': u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
        u'sub_component': u'[set_severity_fields] [get_kpi] [56635]',
        u'orig_index': u'_internal',
        u'event_id': u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
        u'_user': u'nobody'
     }
]

UPDATE_BLOB = [u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f', u'031f06c0-e453-11e7-b054-acbc32b4d98f']

CREATE_TAG = {u'_key': u'5a4c14fb9693fb9dbf20acc1'}

GET_ALL_TAGS = [
    {
        u'mod_time': 1514935547.35519,
        u'event_id': u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
        u'object_type': u'notable_event_tag',
        u'tag_name': u'test',
        u'_key': u'5a4c14fb9693fb9dbf20acc1',
        u'_owner': u'nobody',
        u'create_time': 1514935547.35519,
        u'user': u'UNDEFINED_USERNAME',
        u'owner': u'UNDEFINED_USERNAME',
        u'_user': u'nobody'
    }
]

CREATE_COMMENT = {u'_key': u'5a4c1b589693fb9dbf20acc2'}

GET_COMMENT = {
    u'comment': u'test',
    u'mod_time': 1514937176.58832,
    u'event_id': u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
    u'object_type': u'notable_event_comment',
    u'_key': u'5a4c1b589693fb9dbf20acc2',
    u'_owner': u'nobody',
    u'create_time': 1514937176.58832,
    u'user': u'UNDEFINED_USERNAME',
    u'owner': u'UNDEFINED_USERNAME',
    u'_user': u'nobody'
}

GET_ALL_COMMENTS = [
  {
    u'comment': u'test1',
    u'mod_time': 1513705929.34797,
    u'event_id': u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
    u'object_type': u'notable_event_comment',
    u'_key': u'5a3951ae9693fbcbf741b3ea',
    u'_owner': u'nobody',
    u'create_time': 1513705902.56624,
    u'user': u'UNDEFINED_USERNAME',
    u'owner': u'UNDEFINED_USERNAME',
    u'_user': u'nobody'
  },
  {
    u'mod_time': 1514937176.58832,
    u'comment': u'test',
    u'event_id': u'e28f6a23-e447-11e7-bf0b-acbc32b4d98f',
    u'object_type': u'notable_event_comment',
    u'_key': u'5a4c1b589693fb9dbf20acc2',
    u'_owner': u'nobody',
    u'create_time': 1514937176.58832,
    u'user': u'UNDEFINED_USERNAME',
    u'owner': u'UNDEFINED_USERNAME',
    u'_user': u'nobody'
  }
]

UPDATE_TICKET_INFO = [u'96948c99-f01a-11e7-8d21-acbc32b4d98f']

GET_GROUP = {
    u'mod_time': 1514939410.21328,
    u'status': u'2',
    u'severity': u'1',
    u'_key': u'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
    u'object_type': u'notable_event_group',
    u'event_id': u'b1362b69-24f1-49bd-a2c4-cf57de6b7e2a',
    u'_owner': u'nobody',
    u'create_time': 1513639105.39,
    u'owner': u'admin',
    u'drilldown': [
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
    }
    ],
    u'_user': u'nobody'
}
