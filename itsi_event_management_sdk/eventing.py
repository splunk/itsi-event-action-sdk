# ${copyright}

"""
Use this module to work with your Events in ITSI!

Due to dependency on a Splunk ITSI module, this module must reside on the same
host where ITSI is currently installed. Eventually, we will be moving to
consuming standard REST interfaces and then it should be OK to move this module
to a different host.
"""

import sys
import json
import time
from copy import deepcopy

from eventing_base import Client, setup_logger

default_logger = setup_logger()


class EventMeta(Client):
    """
    Import this class to get information about ITSI Events.
    - What are all the available status values I can set on an Event?
    - What are all the available owners I can have for an Event?
    - What are all the available severities I can set on an Event?

    Usage:
    >>> meta = EventMeta(username, password, base_url)

    Provide your own logger if you want to, else we'll default to default_logger
    """
    def __init__(self, username, password, base_url, logger=default_logger, session=None,
                 silent=False, delay=0.0):

        """
        @type username: string
        @param username: Splunk username

        @type password: string
        @param password: splunk password
        
        @type base_url: string
        @param base_url: splunkd URL

        @type logger: object of type logger
        @param logger: if you have an existing logger, pass it in, we'll log
            stuff there...else check we'll use our own

        @type session: <class 'requests.sessions.Session'> object
        @param session: (optional) In case there's already a session
        
        @type silent: boolean
        @param silent: (optional) When ``True`, any exception resulted
            from HTTP status codes or parsing will be ignored.

        @type delay: float
        @param delay: (option) Ensures a minimum delay of seconds between
            requests.
        """
        super(EventMeta, self).__init__(username, password, base_url, logger, session,
                 silent, delay)
        self.all_info = self.request('GET',
                'event_management_interface/notable_event_configuration/all_info')

    def get_all_statuses(self):
        """
        get all possible valid status values for a Notable Event
        Ex: `open`, `closed`, 'in progress`, `assigned` etc...

        @rtype: list
        @return: list of all possible configured statuses
        #
        """
        return self.all_info.get('statuses', [])

    def get_all_severities(self):
        """
        get all possible valid severity values for a Notable Event
        Ex: `high`, `critical` and so on...

        @rtype: list
        @return: list of all possible configured severities
        """
        return self.all_info.get('severities', [])

    def get_all_owners(self):
        """
        get all posibble valid owner values for a Notable Event
        Ex: `foo`, `bar`, `mr. booboo`

        @rtype: list
        @return: list of all possible configured owners
        """
        return self.all_info.get('owners', [])

class Event(Client):
    """
    Import this class to operate on ITSI Events.
    """
    def __init__(self, username, password, base_url, logger=default_logger, session=None,
                 silent=False, delay=0.0):

        """
        @type username: string
        @param username: Splunk username

        @type password: string
        @param password: splunk password
        
        @type base_url: string
        @param base_url: splunkd URL

        @type logger: object of type logger
        @param logger: if you have an existing logger, pass it in, we'll log
            stuff there...else check we'll use our own

        @type session: <class 'requests.sessions.Session'> object
        @param session: (optional) In case there's already a session
        
        @type silent: boolean
        @param silent: (optional) When ``True`, any exception resulted
            from HTTP status codes or parsing will be ignored.

        @type delay: float
        @param delay: (option) Ensures a minimum delay of seconds between
            requests.
        """
        super(Event, self).__init__(username, password, base_url, logger, session,
                                    silent, delay)

    def _get_object(self, object_):
        """
        given an object, try to get a dict/list type
        merely a wrapper to json.loads(). doesnt crap out and returns None if
        invalid.
        @param object_: input object, any type
        @return dict/list if valid, None if otherwise
        """
        rval = None
        if isinstance(object_, basestring):
            try:
                rval = json.loads(object_)
            except Exception:
                pass
        elif isinstance(object_, dict):
            rval = object_
        elif isinstance(object_, list):
            rval = object_
            
        return rval

    def _extract(self, objects, key):
        """
        given a list of objects, extract requested values given key, dedup
        and return a list
        @type objects: dict/list
        @param objects: objects to iterate over and extract id from
        @type key: basestring
        @param key: `key` that corresponds to the id
        @return a list of object ids
        @raises Exception
        """
        ids_ = []

        # always work with list
        objects = self._get_object(objects)
        if not objects:
            return ids_

        if isinstance(objects, dict):
            objects = [objects]
        if not isinstance(objects, list):
            raise Exception('Expecting `objects` to be list/dict type and not `%s`'
                    % type(objects).__name__)
        for i in objects:
            if i.get(key):
                ids_.append(i[key])
                
        return list(set(ids_))

    def _get_from_index(self, event_ids, split_by="," , **kwargs):
        """
        given an id or list of ids, return a dictionary of pertinent fields
        for that event. This method runs a Splunk search.

        @type event_id: str
        @param event_id: a unique id for an event

        @type split_by: str
        @param split_by: if event_ids is of type basestring, we will split it
        into many event ids into a list. What is the separator? Defaults to `,`

        @type kwargs: dict
        @param kwargs: send in keys `earliest_time` and
        `latest_time` with corresponding values if you know what you are doing.
            Ex:
            '-15m' implies '15 mins ago'
            '-15s' implies '15 seconds ago'
            '-15d' implies '15 days ago'
            '-15w' implies '15 weeks ago'
            'rt' implies real time
            'now' implies current time
            no other values are supported

        @return a valid Dict if event is found; None if no resource is found
        """
        if isinstance(event_ids, basestring):
            event_ids = event_ids.split(',')

        if not isinstance(event_ids, list):
            raise TypeError('Expecting event_ids to be a string or list')

        # we only care about `earliest_time` and `latest_time`. get rid of other
        # keys
        supported_params = ('earliest_time', 'latest_time')
        for i in kwargs.keys():
            kwargs.pop(i) if i not in supported_params else None

        objects = None

        # indexing takes time and just because we have an event_id does not
        # really means that event has been indexed
        retries = 10
        while retries:
            time.sleep(5)
            try:
                params = {'ids':json.dumps(event_ids)}
                params.update(kwargs)
                objects = self.request('GET', 'event_management_interface/notable_event',
                        params=params)
                if objects:
                    break
                retries -= 1
            except Exception:
                self.logger.exception('Internal Error.')
                break
            
        return objects

    def get_severity(self, events=None, event_ids=None, split_by=",", **kwargs):
        """
        given a list of event ids, return their severities
        @type events: list of dicts
        @param events: each dict in the list represents an event that was sent
            to us by Splunk as an outcome of a Custom Action. the get_event()
            method in class CustomEventActionBase generates such an item.
        High performant.

        @type event_ids: str or list
        @param event_ids: a unique id of an event or list of event ids of events
        Less performant.

        @type split_by: str
        @param split_by: if `event_ids` is of type basestring, we will split it
        into many event ids;into a list. What is the separator? Defaults to `,`

        @type kwargs: dict
        @param kwargs: send in keys `earliest_time` and
        `latest_time` with corresponding values if you know what you are doing.
            Ex:
            '-15m' implies '15 mins ago'
            '-15s' implies '15 seconds ago'
            '-15d' implies '15 days ago'
            '-15w' implies '15 weeks ago'
            'rt' implies real time
            'now' implies current time
            no other values are supported

        @return a list of tuples (event_id: severity) on valid request
        None on invalid request.
        """
        # validate + normalize
        if not events and not event_ids:
            raise ValueError(('Expecting either `events` or `event_ids`. Both'
                ' are None.'))
        if events and isinstance(events, dict):
            events = [events]
        if events and not isinstance(events, list):
            raise TypeError(('Invalid type for `events`. Expecting list.'
                ' Received type: {}').format(type(events).__name__))

        if events:
            event_ids = self._extract(events, 'event_id')
        else:
            # we have event_ids, lets fetch events from index
            if isinstance(event_ids, basestring):
                event_ids = event_ids.split(split_by)
            if not isinstance(event_ids, list):
                return None
            events = self._get_from_index(event_ids, **kwargs)
            if not events:
                return None
        severities = self._extract(events, 'severity')
        
        return zip(event_ids, severities)

    def get_status(self, events=None, event_ids=None, split_by=",", **kwargs):
        """
        given a list of events or event ids, return their statuses

        @type events: list of dicts
        @param events: each dict in the list represents an event that was sent
            to us by Splunk as an outcome of a Custom Action. the get_event()
            method in class CustomEventActionBase generates such an item.
        High performant.

        @type event_ids: basestring/list
        @param event_ids: a unique id for an event or a list of them
        Less performant.

        @type split_by: str
        @param split_by: if `event_ids` is of type basestring, we will split it
        into many event ids;into a list. What is the separator? Defaults to `,`

        @type kwargs: dict
        @param kwargs: send in keys `earliest_time` and
        `latest_time` with corresponding values if you know what you are doing.
            Ex:
            '-15m' implies '15 mins ago'
            '-15s' implies '15 seconds ago'
            '-15d' implies '15 days ago'
            '-15w' implies '15 weeks ago'
            'rt' implies real time
            'now' implies current time
            no other values are supported

        @return a list of tuples (event_id: severity) on valid request
        None on an invalid request
        """
        # validate + normalize
        if not events and not event_ids:
            raise ValueError(('Expecting either `events` or `event_ids`. Both'
                ' are None.'))
        if events and isinstance(events, dict):
            events = [events]
        if events and not isinstance(events, list):
            raise TypeError(('Invalid type for `events`. Expecting list.'
                    ' Received type: {}').format(type(events).__name__))

        if events:
            event_ids = self._extract(events, 'event_id')
        else:
            # We have event_ids, lets fetch events from index
            if isinstance(event_ids, basestring):
                event_ids = event_ids.split(split_by)
            if not isinstance(event_ids, list):
                return None
            events = self._get_from_index(event_ids, **kwargs)
            if not events:
                return None

        statuses = self._extract(events, 'status')
        
        return zip(event_ids, statuses)

    def get_owner(self, events=None, event_ids=None, split_by=",", **kwargs):
        """
        given an event id, return its owner

        @type events: list of dicts
        @param events: each dict in the list represents an event that was sent
            to us by Splunk as an outcome of a Custom Action. the get_event()
            method in class CustomEventActionBase generates such an item.
        High performant.

        @type event_ids: basestring/list
        @param event_ids: a unique id for an event or a list of them
        Less performant.

        @type split_by: str
        @param split_by: if `event_ids` is of type basestring, we will split it
        into many event ids; into a list. What is the separator? Defaults to `,`

        @type kwargs: dict
        @param kwargs: send in keys `earliest_time` and
        `latest_time` with corresponding values if you know what you are doing.
            Ex:
            '-15m' implies '15 mins ago'
            '-15s' implies '15 seconds ago'
            '-15d' implies '15 days ago'
            '-15w' implies '15 weeks ago'
            'rt' implies real time
            'now' implies current time
            no other values are supported

        @rtype: list of tuples
        @return: [(event_id, owner)] if valid. None if invalid.
        """
        # validate + normalize
        if not events and not event_ids:
            raise ValueError(('Expecting either `events` or `event_ids`. Both'
                    ' are None.'))
        if events and isinstance(events, dict):
            events = [events]
        if events and not isinstance(events, list):
            raise TypeError(('Invalid type for `events`. Expecting list.'
                    ' Received type: {}').format(type(events).__name__))

        # normalization complete....
        if events:
            # get event_ids from these events...
            event_ids = self._extract(events, 'event_id')
        else:
            # we have event_ids, lets fetch events from index
            if isinstance(event_ids, basestring):
                event_ids = event_ids.split(split_by)
            if not isinstance(event_ids, list):
                return None
            events = self._get_from_index(event_ids, **kwargs)
            if not events:
                return None

        # extract owners now that we have events...
        owners = self._extract(events, 'owner')
        
        return zip(event_ids, owners)

    def update(self, blob, split_by=',', **kwargs):
        """
        update each event id in `blob` with given data value individually
        This method only deals with updating `status`, `severity` and `owner`

        To update tags and comments, use `update_tag()` and `update_comment()`
        Why separate methods? This is an implementation *secret*.

        @type blob: dict
        @param blob:
            [
                {
                    'event_ids': ['event_id1', 'event_ida', ... ],
                    'severity': 'high',
                    'status': 'closed',
                    'owner': 'cottonmouth'
                },
                {
                    'event_ids': ['event_id2', 'event_idb', ... ],
                    'severity': 'critical',
                    'status': 'open',
                    'owner': 'black_mamba'
                },
                ...
            ]
        @type kwargs: dict
        @param kwargs: send in keys `earliest_time` and
        `latest_time` with corresponding values if you know what you are doing.
            Ex:
            '-15m' implies '15 mins ago'
            '-15s' implies '15 seconds ago'
            '-15d' implies '15 days ago'
            '-15w' implies '15 weeks ago'
            'rt' implies real time
            'now' implies current time
            no other values are supported

        @rtype: list
        @return: list of updated events
        """
        if isinstance(blob, dict):
            blob = [blob]
        if not isinstance(blob, list):
            raise TypeError(('Expecting `blob` to be a dict/list. Received:'
                    ' %s')%type(blob).__name__)

        if not blob:
            raise ValueError('Expecting `blob` to be non-empty.')

        rval = []
        for group in blob:
            # validate/sanitize...
            if not isinstance(group, dict):
                raise TypeError(('Expecting a dict. Received: '
                        '`%s`. Type: `%s`')%(group, type(group).__name__))
            if 'event_ids' not in group:
                raise KeyError('Expecting `event_ids` in your input.')
            keys = group.pop('event_ids')

            # sanitize request, get rid of unsupported keys...
            supported_keys = ('owner', 'severity', 'status', 'event_ids')
            for k in group.keys():
                if k not in supported_keys:
                    self.logger.info('Getting rid of `%s`: `%s`. Unsupported.'%(k, group[k]))
                    group.pop(k)

            if isinstance(keys, basestring):
                keys = keys.split(split_by)
            data = []
            for i in keys:
                event_data = deepcopy(group)
                event_data['event_id'] = i
                data.append(event_data)
            self.logger.info('Updating keys: `%s` with: %s. kwargs: %s',
                    keys, data, kwargs)
            objects = self.request('PUT', 'event_management_interface/notable_event',
                    params=kwargs, data=data)
            rval.extend(objects)
            
        return rval

    def update_severity(self, event_ids, severity, split_by=',', **kwargs):
        """
        given list of event ids, update each of its severity to given
        severity value.
        @type event_ids: basestring/list
        @param event_ids: comma separated event ids or list of event ids

        @type severity: basestring
        @param severity: one of the many supported severity values

        @type split_by: basestring
        @param split_by: if `event_ids` is a string, what are the event ids split
        by? defaults to `,`

        @type kwargs: dict
        @param kwargs: other time specific params like `earliest_time` and
        `latest_time` to locate your event. Pass nothing if you dont know these
        values.

        @rtype: list
        @return: updated notable event
        """
        if isinstance(event_ids, basestring):
            if not event_ids.strip():
                raise ValueError(('Expecting `event_ids` to contain some value.'
                        ' Received: %s')%event_ids)
            event_ids = event_ids.split(split_by)
        if not isinstance(event_ids, list):
            raise TypeError(('Expecting `event_ids` to be of type basestring/'
                    'list. Received: {}. Type: {}').format(event_ids,
                    type(event_ids).__name__))
        if not event_ids or not severity.strip():
            raise ValueError(('Expecting non-empty list of `event_ids`. and valid'
                    ' severity string'))

        data = []
        for i in event_ids:
            data.append({'severity':severity, 'event_id': i})

        self.logger.info('Updating keys: `%s` with: %s. kwargs: %s',
                event_ids, data, kwargs)
        objects = self.request('PUT', 'event_management_interface/notable_event', 
                params=kwargs, data=data)
        
        return objects

    def update_status(self, event_ids, status, split_by=',', **kwargs):
        """
        given list of event ids, update each of its status to given
        value.
        @type event_ids: basestring/list
        @param event_ids: comma separated event ids or list of event ids

        @type status: basestring
        @param status: value of the new status

        @type split_by: basestring
        @param split_by: if `event_ids` is a string, what are the event ids split
        by? defaults to `,`

        @type kwargs: dict
        @param kwargs: other time specific params like `earliest_time` and
        `latest_time` to locate your event. Pass nothing if you dont know these
        values.

        @rtype: list
        @return: updated notable event
        """
        if isinstance(event_ids, basestring):
            if not event_ids.strip():
                raise ValueError(('Expecting `event_ids` to contain some value.'
                        ' Received: {}').format(event_ids))
            event_ids = event_ids.split(split_by)
        if not isinstance(event_ids, list):
            raise TypeError(('Expecting `event_ids` to be of type basestring/'
                    'list. Received: {}. Type: {}').format(event_ids,
                    type(event_ids).__name__))
        if not event_ids or not status.strip():
            raise ValueError(('Expecting non-empty list of `event_ids`. and valid'
                    ' status string'))

        data = []
        for i in event_ids:
            data.append({'status': status, 'event_id': i})

        self.logger.info('Updating keys: `%s` with: %s. kwargs: %s',
                event_ids, data, kwargs)
        objects = self.request('PUT', 'event_management_interface/notable_event', 
                params=kwargs, data=data)
        
        return objects

    def update_owner(self, event_ids, owner, split_by=',', **kwargs):
        """given list of event ids, update each of its owner to given
        value.
        @type event_ids: basestring/list
        @param event_ids: comma separated event ids or list of event ids

        @type owner: basestring
        @param owner: value of the new owner

        @type split_by: basestring
        @param split_by: if `event_ids` is a string, what are the event ids split
        by? defaults to `,`

        @type kwargs: dict
        @param kwargs: other time specific params like `earliest_time` and
        `latest_time` to locate your event. Pass nothing if you dont know these
        values.

        @rtype: list
        @return: updated notable event
        """
        if isinstance(event_ids, basestring):
            if not event_ids.strip():
                raise ValueError(('Expecting `event_ids` to contain some value.'
                        ' Received: %s')%event_ids)
            event_ids = event_ids.split(split_by)
        if not isinstance(event_ids, list):
            raise TypeError(('Expecting `event_ids` to be of type basestring/'
                    'list. Received: %s. Type: %s')%(event_ids, type(event_ids).__name__))
        if not event_ids or not owner.strip():
            raise ValueError(('Expecting non-empty list of `event_ids`. and valid'
                    ' owner string'))
        data = []
        for i in event_ids:
            data.append({'owner': owner, 'event_id': i})

        self.logger.info('Updating keys: `%s` with: %s. kwargs: %s',
                event_ids, data, kwargs)
        objects = self.request('PUT', 'event_management_interface/notable_event', 
                params=kwargs, data=data)
        
        return objects

    def create_tag(self, event_id, tag_value):
        """
        create a tag for given event_id

        @type event_id: str
        @param event_id: id of an event

        @type tag_value: str
        @param tag_value: new value of this tag

        @rtype: dict
        @return a nicely formatted dictionary/None on failure.
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                    ' basestring. Received: %s')%event_id)
        if not isinstance(tag_value, basestring):
            raise TypeError(('Expecting `tag_value` to be non-empty'
                    ' basestring. Received: %s')%tag_value)
        data = {'event_id': event_id, 'tag_name': tag_value}

        objects = self.request('POST', 'event_management_interface/notable_event_tag',
                data=data)

        if any([
            not isinstance(objects, dict),
            isinstance(objects, dict) and '_key' not in objects]):
            self.logger.error('Unable to create requested tag for event_id: `%s`.\
                    tag_value: `%s`',event_id, tag_value)
            return None

        return {
            'event_id':event_id,
            'tag_id': objects['_key'],
            'tag_name': tag_value
            }

    def update_tag(self, event_id, tag_id, tag_value):
        """
        given  an event id, a tag_id update the existing tag.
        An event can have more than one tag.
        Each tag has an id. Hence the tag id! For a given event, no duplicate
        tags will be allowed.

        @type event_id: str
        @param event_id: id of an event

        @type tag_id: str
        @param tag_id: id of the tag

        @type tag_value: str
        @param tag_value: new value of this tag

        @rtype dict:
        @return committed value...
        """ 
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                ' basestring. Received: %s')%event_id)
        if not isinstance(tag_id, basestring):
            raise TypeError(('Expecting `tag_id` to be non-empty'
                ' basestring. Received: %s')%tag_id)
        data = {
            'event_id': event_id,
            '_key': tag_id,
            'tag_name': tag_value
            }
        objects = self.request('PUT', 'event_management_interface/notable_event_tag',
                data=data)
        
        return objects

    def get_all_tags(self, event_id):
        """
        given an event_id, fetch all of its tags
        @type event_id: str
        @param event_id: id of an event

        @rtype: list
        @return: list of all existing tags for a given event.
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                ' basestring. Received: %s')%event_id)
        extension = 'event_management_interface/notable_event_tag/{}'.format(str(event_id))
        objects = self.request('GET', extension, params={'is_event_id': True})
        tags = self._extract(objects, 'tag_name')
        
        return tags

    def get_tag(self, tag_id):
        """
        given a tag id, fetch its value
        @type tag_id: str
        @param tag_id: id of desired tag

        @rtype: basestring
        @return: tag value corresponding to `tag_id`
        """
        if not isinstance(tag_id, basestring):
            raise TypeError(('Expecting `tag_id` to be non-empty'
                    ' basestring. Received: %s')%tag_id)
        extension = 'event_management_interface/notable_event_tag/{}'.format(str(tag_id))
        objects = self.request('GET', extension)
        tag = self._extract(objects, 'tag_name')
        
        if tag:
            return tag[0]
        else:
            return None
        
    def delete_tag(self, tag_id):
        """
        given a tag_id, delete its value
        @type tag_id: str
        @param tag_id: id of the tag you are interested in deleting in.
        @return nothing
        """
        if not isinstance(tag_id, basestring):
            raise TypeError(('Expecting `tag_id` to be non-empty'
                    ' basestring. Received: %s')%tag_id)
        extension = 'event_management_interface/notable_event_tag/{}'.format(str(tag_id))
        objects = self.request('DELETE', extension)
        return

    def delete_all_tags(self, event_id):
        """
        given an event_id, delete all of its tags
        @type event_id: str
        @param event_id: id of the event whose tags you want to delete
        @return nothing
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                    ' basestring. Received: %s')%event_id)
        extension = 'event_management_interface/notable_event_tag/{}'.format(str(event_id))
        objects = self.request('DELETE', extension, params={'is_event_id': True})
        return

    def create_comment(self, event_id, comment):
        """
        for given event_id, add a new comment
        @type event_id: str
        @param event_id: id of the event you want to add a comment to

        @type comment: str
        @param comment: the comment you wish to add

        @rtype: dict
        @return: a nicely formatted dict consisting of comment, comment id and
        event id
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                    ' basestring. Received: %s')%event_id)
        if not isinstance(comment, basestring):
            raise TypeError(('Expecting `comment` to be non-empty'
                    ' basestring. Received: %s')%comment)
        data = {
                'event_id': event_id,
                'comment': comment
                }
        objects = self.request('POST', 'event_management_interface/notable_event_comment',
                data=data)
        if not objects:
           self.logger.error('Unable to create requested comment `%s` for event id: `%s`',
                    comment, event_id)
           return None

        rval = {
            'event_id': event_id,
            'comment_id': objects.get('_key'),
            'comment': comment
            }
        self.logger.info('Successfully created comment: `%s` for event id: `%s`.\
                comment id: `%s`', comment, event_id, objects.get('_key'))
        return rval

    def get_comment(self, comment_id):
        """
        for a given comment id, fetch the comment
        @type comment_id: str
        @param comment_id: id of the comment we care about

        @rtype: str
        @return: comment corresponding to comment id
        """
        if not isinstance(comment_id, basestring):
            raise TypeError(('Expecting `comment_id` to be non-empty'
                    ' basestring. Received: %s')%comment_id)
        extension = 'event_management_interface/notable_event_comment/{}'.format(str(comment_id))
        objects = self.request('GET', extension)
        comment = self._extract(objects, 'comment')
        return comment[0] if comment else ''

    def get_all_comments(self, event_id):
        """
        for a given event id, fetch all of its comments
        @type event_id: str
        @param event_id: id of the event we care about

        @rtype: list
        @return: list of comments corresponding to event_id
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                    ' basestring. Received: %s')%event_id)
        extension = 'event_management_interface/notable_event_comment/{}'.format(str(event_id))
        objects = self.request('GET', extension, params={'is_event_id': True})
        comments = self._extract(objects, 'comment')
        return comments

    def delete_comment(self, comment_id):
        """
        delete the comment associated with comment id
        @type comment_id: str
        @param comment_id: id of the comment we care about

        @returns: nothing
        """
        if not isinstance(comment_id, basestring):
            raise TypeError(('Expecting `comment_id` to be non-empty'
                    ' basestring. Received: %s')%comment_id)
        extension = 'event_management_interface/notable_event_comment/{}'.format(str(comment_id))
        objects = self.request('DELETE', extension)
        return

    def delete_all_comments(self, event_id):
        """
        delete all comments associated with event id
        @type event_id: str
        @param event_id: id of the event we care about

        @returns nothing
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                    ' basestring. Received: %s')%event_id)
        extension = 'event_management_interface/notable_event_comment/{}'.format(str(event_id))
        objects = self.request('DELETE', extension, params={'is_event_id': True})
        return

    def update_comment(self, event_id, comment_id, comment):
        """
        given  an event id, a comment_id update the comment.
        An event can have more than one comment.
        Each comment has an id. Hence the event id! For a given event, no duplicate
        comments will be allowed.

        @type event_id: str
        @param event_id: id of an event

        @type comment_id: str
        @param comment_id: id of the comment

        @type comment: str
        @param comment: new value of this comment

        @rtype dict:
        @return committed value...
        """
        if not isinstance(event_id, basestring):
            raise TypeError(('Expecting `event_id` to be non-empty'
                    ' basestring. Received: %s')%event_id)
        if not isinstance(comment_id, basestring):
            raise TypeError(('Expecting `tag_id` to be non-empty'
                    ' basestring. Received: %s')%comment_id)
        data = {
                'event_id': event_id,
                '_key': comment_id,
                'comment': comment
                }
        objects = self.request('PUT', 'event_management_interface/notable_event_comment',
            data=data)
        return objects

    def update_ticket_info(self, event_ids, ticket_system, ticket_id,
            ticket_url, **other_params):
        """ 
        given a list of event_ids, update each of them with an external
        ticket info
        @type event_ids: list/basestring
        @param event_ids: list of event_ids or comma separated string of
        event_ids

        @type ticket_system: basestring
        @param ticket_system: string representing an external ticket system
            Ex: Remedy, Siebel, ServiceNow etc...

        @type ticket_id: basestring
        @param ticket_id: identifier of an external ticket.

        @type ticket_url: basestring
        @param ticket_url: url to reach external ticket.

        @type other_params: dict
        @param other_params: other key value pairs to locate your event.
            Pass nothing if you dont know these values.

        @rtype dict:
        @return: dict with list of ticket ids that are successfully updated
        and list of ticket ids that were fail to update.

        """
        if isinstance(event_ids, basestring):
            event_ids = event_ids.split(',')
        if not isinstance(event_ids, list):
            raise TypeError('Expecting event_ids to be a list type.\
                    Received=%s'%type(event_ids).__name__)
        if not event_ids:
            raise ValueError('Expecting event_ids to have atleast 1 id. Received=%s'%event_ids)

        self.logger.info(('Event ids=%s ticket_system=%s ticket_id=%s'
                ' ticket_url=%s other params=%s'), event_ids, ticket_system
                ,ticket_id, ticket_url, json.dumps(other_params))

        for id_ in event_ids:
            data = {
                "ticket_system": ticket_system,
                "ticket_url": ticket_url,
                "ticket_id": ticket_id
            }
            data.update(other_params)
            extension = 'event_management_interface/ticketing/{}'.format(str(id_))
            objects = self.request('PUT', extension, data=data)
        
        return objects

    def delete_ticket_info(self, event_ids, ticket_system, ticket_id):
        """
        Delete external ticketing based information for given event_ids
        @type event_ids: list/basestring
        @param event_ids: list of event_ids or comma separated string of
        event_ids

        @type ticket_system: basestring
        @param ticket_system: string representing an external ticket system
            Ex: Remedy, Siebel, ServiceNow etc...
        Set ticket_system to None to delete all tickets for these event_ids

        @type ticket_id: basestring
        @param ticket_id: identifier of an external ticket.
        Set ticket_id to None to delete all tickets for this ticket_system

        @rtype dict:
        @return: dict with list of ticket ids that are successfully deleted
        and list of ticket ids that were fail to delete.

        """
        if isinstance(event_ids, basestring):
            event_ids = event_ids.split(',')
        if not isinstance(event_ids, list):
            raise TypeError('Expecting event_ids to be a list type. Received={}'.format(
                    type(event_ids).__name__))
        if not event_ids:
            raise ValueError('Expecting event_ids to have atleast 1 id. Received={}'.format(
                    event_ids))
        self.logger.info(('Event ids=%s ticket_system=%s ticket_id=%s'
                ' ticket_url=%s other params=%s'), event_ids, ticket_system
                ,ticket_id)

        for id_ in event_ids:
            extension = 'event_management_interface/ticketing/{}/{}/{}'\
                    .format(str(id_), ticket_system, str(ticket_id))
            objects = self.request('DELETE', extension)

        return objects


class EventGroup(Client):
    """
    Import this class to operate on ITSI Event Group.
    """
    def __init__(self, username, password, base_url, logger=default_logger, session=None,
                 silent=False, delay=0.0):

        """
        @type username: string
        @param username: Splunk username

        @type password: string
        @param password: splunk password
        
        @type base_url: string
        @param base_url: splunkd URL

        @type logger: object of type logger
        @param logger: if you have an existing logger, pass it in, we'll log
            stuff there...else check we'll use our own

        @type session: <class 'requests.sessions.Session'> object
        @param session: (optional) In case there's already a session
        
        @type silent: boolean
        @param silent: (optional) When ``True`, any exception resulted
            from HTTP status codes or parsing will be ignored.

        @type delay: float
        @param delay: (option) Ensures a minimum delay of seconds between
            requests.
        """
        super(EventGroup, self).__init__(username, password, base_url, logger, session,
                                         silent, delay)

        
    def is_valid_drilldown(self, drilldown):
        """
        Validation for drilldown link
        Must have name and the link
        And all values must be a string

        @type drilldown: dict
        @param drilldown: drilldown to be added

        @rtype: bool
        @return: True or false according to validation.
        """
        if type(drilldown) is not dict:
            return False

        VALID_FIELD = ['name', 'link']

        for field in VALID_FIELD:
            if field not in drilldown:
                return False
            if not drilldown.get(field):
                return False
            if type(drilldown.get(field)) is not str:
                return False

        return True

    def _clean_drilldown(self, drilldown):
        """
        Remove all non-whitelisted fields from drilldown dict

        @type drilldown: dict
        @param drilldown: drilldown to clean

        @rtype: dict
        @return: cleaned drilldown
        """
        whitelisted_fields = [
            'name',
            'link'
        ]

        for key in drilldown.keys():
            if key not in whitelisted_fields:
                del drilldown[key]

        return drilldown

    def _find_drilldown(self, drilldown_list, drilldown):
        """
        Find drilldown in drilldown list by name

        @type drilldown_list: list
        @param drilldown_list: list of drilldowns

        @type drilldown: dict
        @param drilldown: drilldown to find

        @rtype: int
        @return: index of found drilldown in drilldown list
        """
        for index, dd in enumerate(drilldown_list):
            if dd['name'] == drilldown['name']:
                return index

        return None

    def add_drilldown(self, group_id, drilldown):
        """
        Adds drilldown to a notable event group.
        @type group_id: string
        @param group_id: id of the group where add_drilldown to be operated on

        @type drilldown: string
        @param drilldown: The drilldown data that wanted to be add to
                        {
                            'name': "DrilldownName",
                            'link': "http://drill.down"
                        }
        """
        if not self.is_valid_drilldown(drilldown):
                raise ValueError('Drilldown data must have link and name')
        clean_drilldown = self._clean_drilldown(drilldown)
        try:
            drilldown_list = self.get(group_id).get('drilldown', [])
        except AttributeError:
            raise TypeError('Group is not of type dict')
        try:
            drilldown_list.append(clean_drilldown)
        except AttributeError:
            raise TypeError('Drilldown field is not of type list')
        data = {'drilldown': drilldown_list,
                'event_id': group_id,
                '_key': group_id
        }
        extension = 'event_management_interface/notable_event_group'
        objects = self.request('PUT', extension, data=data)
        
        return objects

    def update_drilldown(self, group_id, drilldown):
        """
        Update a drilldown for a NotableEventGroup

        @type group_id: string
        @param group_id: id of the group who owns the drilldown to be updated

        @type drilldown: dict
        @param drilldown: drilldown to be updated
        """
        if not self.is_valid_drilldown(drilldown):
            raise ValueError('Drilldown data must have link and name')
        group = self.get(group_id)
        if not group:
            raise ValueError('Group does not exist')
        clean_drilldown = self._clean_drilldown(drilldown)
        try:
            drilldown_list = group.get('drilldown', [])
        except AttributeError:
            raise TypeError('Group is not of type dict')
        drilldown_index = self._find_drilldown(drilldown_list, clean_drilldown)
        if not drilldown_list or drilldown_index is None:
            response = self.add_drilldown(group_id, drilldown)
            return response
        try:
            drilldown_list[drilldown_index].update(clean_drilldown)
        except IndexError:
            raise IndexError('Drilldown index of: {0} out of bounds\
                    drilldown list'.format(drilldown_index))
        except ValueError:
            raise ValueError('Nondictionary type given for drilldown')
        except TypeError:
            raise TypeError('Drilldown index given is not an integer')
        except AttributeError:
            raise AttributeError('Drilldown list item at index: {0}\
                    is not of type dict'.format(drilldown_index))
        data = {'drilldown': drilldown_list,
                'event_id': group_id,
                '_key': group_id
        }
        extension = 'event_management_interface/notable_event_group'
        objects = self.request('PUT', extension, data=data)

        return objects

    def delete_drilldown(self, group_id, drilldown):
        """
        Delete a drilldown for a NotableEventGroup

        @type group_id: string
        @param group_id: id of the group who owns the drilldown to be deleted

        @type drilldown: dict
        @param drilldown: drilldown to be deleted
        """

        if not self.is_valid_drilldown(drilldown):
            raise ValueError('Drilldown data must have link and name')
        group = self.get(group_id)
        if not group:
            raise ValueError('Group does not exist')
        clean_drilldown = self._clean_drilldown(drilldown)
        try:
            drilldown_list = group.get('drilldown', [])
        except AttributeError:
            raise TypeError('Group is not of type dict')
        drilldown_index = self._find_drilldown(drilldown_list, clean_drilldown)
        if drilldown_index is None:
            raise KeyError('Drilldown with name: {0} not found'.format(drilldown['name']))
        try:
            drilldown_list.pop(drilldown_index)
        except AttributeError:
            raise AttributeError('Drilldown list is not of type list')
        except TypeError:
            raise TypeError('Drilldown index given is not an integer')
        except IndexError:
            raise IndexError('Drilldown index of: {0} out of bounds for\
                    drilldown list'.format(drilldown_index))

        data = {'drilldown': drilldown_list,
                'event_id': group_id,
                '_key': group_id
        }
        extension = 'event_management_interface/notable_event_group'
        objects = self.request('PUT', extension, data=data)

        return objects

    def get(self, group_id):
        """
        Get the EventGroup Object
        @type group_id: string
        @param group_id: id of the group where add_drilldown to be operated on
        """
        extension = 'event_management_interface/notable_event_group/{}'.format(str(group_id))
        objects = self.request('GET', extension)
        return objects
