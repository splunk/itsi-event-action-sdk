# Copyright (C) 2005-2018 Splunk Inc. All Rights Reserved

"""
Import this module when you'd like to consume output of your modalert
All the details are abstracted nicely for you.
"""

import os
import csv
import json
import gzip

from eventing_base import setup_logger

default_logger = setup_logger()

class CustomEventActionBase(object):
    """
    In your script, inherit your class from this class.
    Use the get_event() method to work on the event which
    triggered your script.

    Usage::
        >>> class MyCustomEventAction(CustomEventActionBase):
        >>>     def __init__(self, settings, logger, **kwargs):
        >>>         super(MyCustomEventAction, self).__init__(settings, logger)
        >>>         # other initializations
        >>>     def execute(self):
        >>>         config = self.get_config()
        >>>         event_data = self.get_event()
        >>>         # implement your logic here...not implemented in baseclass.
    """
    def __init__(self, settings, logger=default_logger):
        """
        Initialize with incoming parameters which were passed to your script
        via stdin.
        @type settings: basestring/dict
        @param settings: Incoming parameters passed to your script via stdin.

        @type logger: logger
        @param logger: Inherited class' logger
        """
        if isinstance(settings, basestring):
            settings = json.loads(settings)
        if not isinstance(settings, dict):
            raise TypeError(('Expecting a JSON serializeable string'
                '. Received=`%s`. Type=`%s`')%(settings, type(settings).__name__))
        self.settings = settings
        self.logger = logger
        self.logger.debug('Received settings=`%s`', self.settings)

    def get_config(self):
        """
        return the config that came with settings
        @rtype: dict
        @return configuration of your modular alert
        """
        return self.settings.get('configuration')

    def get_session(self):
        """
        return the splunk session key
        @rtype: basestring
        @return: splunkd session key / auth token
        """
        if 'session' not in self.settings:
            self.logger.error('No session found in settings=`%s`',self.settings)
            raise KeyError('No session found in settings')
        return self.settings['session']

    def get_results_file(self):
        """
        return the results file. Results file is where the results are
        temporarily stored

        @rtype: basestring
        @return: the location/os.path of the results file.
        """
        if 'results_file' not in self.settings:
            self.logger.error('No results_file found in settings=`%s`',self.settings)
            raise KeyError('No results_file found in settings')
        return self.settings['results_file']

    def get_event(self):
        """
        Get events which triggered our custom action.
        Assumes that output of `sendalert` is always a .csv.gz
        Implemented as a generator because we could potentially be working on
        thousands of events.

        @rtype: dict
        @returns: yields a dict type object till all received events are
        returned.
        """
        file_path = self.get_results_file()

        # do stuff only if there is a results file...
        if not file_path:
            self.logger.debug('Invalid file path. received=%s', file_path)
            yield ValueError('Expecting a valid file path. Received=`%s`'%file_path)

        if not os.path.exists(file_path):
            self.logger.debug('File=`%s` does not exist.', file_path)
            yield IOError('File=`%s` does not exist.' % file_path)

        with gzip.open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row

    def extract_event_id(self, notable_data):
        """
        given notable_data extract event_id
        @type notable_data: basestring
        @param notable_data: notable event object from which we try to extract
            event_id
        @rtype: basestring/NoneType
        @return: event_id/None
        """
        if notable_data is None:
            raise TypeError('No notable_data received')

        if not isinstance(notable_data, dict):
            try:
                notable_data = json.loads(notable_data)
            except (TypeError, ValueError) as exc:
                self.logger.exception(exc)
                msg = ('We will only work with JSON type data. '
                    'Received: {}. Type: {}').format(notable_data,
                            type(notable_data).__name__)
                self.logger.error(msg)
                raise Exception(msg)
        return notable_data.get('event_id')

    def execute(self):
        """
        Not Implemented. Derived class must implement this method. This is
        where the custom action does stuff such as:
        - Create a ticket
        - Write a worklog update as a comment
        - Tag your ITSI event with stuff like `remedy` or `snow` or `siebel` or
          whatever...
        - update the owner of the event
        - update the severity of the event
        - update the status of the event
        ...and so on.
        """
        raise NotImplementedError('Derived class must implemented `execute`.')
