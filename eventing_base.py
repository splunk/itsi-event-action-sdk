# $ {copyright}
"""
SDK's Base.
Define Base Classes applicable for all Event Management here.
Importing this module is pretty useless.
The pertinent classes for you are probably in sub directories in this directory.
"""

from splunk.auth import getSessionKey

class EventBase(object):
    '''All SDK classes to inherit this as their base class
    tracks stuff like Splunk session key, logger info and so on...
    '''
    def __init__(self, session_key, username=None, password=None, logger=None):
        if session_key:
            if not isinstance(session_key, basestring):
                raise TypeError('session_key must be string of non-zero length.')
            if not session_key.strip():
                raise ValueError('session_key must be a non-zero length string.')
        else:
            if any([
                not (username or password),
                not (isinstance(username, basestring) or \
                    isinstance(password, basestring)),
                isinstance(username, basestring) and not username.strip(),
                isinstance(password, basestring) and not password.strip()
                ]):
                raise ValueError(('In the absense of session_key, expecting a valid '
                    ' non empty string, for both your username and password.'))
            session_key = getSessionKey(username, password)
            if not session_key:
                raise TypeError(('Login failed. Seems like some credentials'
                        ' issue.'))
        self.session_key = session_key
        self.logger = logger
