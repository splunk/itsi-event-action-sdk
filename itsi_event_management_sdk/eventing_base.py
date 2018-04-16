# $ {copyright}
"""
SDK's Client class.
Define Base Classes applicable for all Event Management here.
"""
import time
import json
import requests
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_name='sdk.log', logger_name='event_managment_sdk', level=logging.INFO):
    default_logger = logging.getLogger(logger_name)
    default_logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(log_name, maxBytes=2500000, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    default_logger.addHandler(file_handler)
    return default_logger

class Client(object):
    '''All SDK classes to inherit this as their base class
    tracks stuff like base_url, session etc.
    '''
    _AVAILABLE_VERSIONS = ('1.0')
    def __init__(self, username, password, base_url, logger, session=None,
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
        self.headers={"Content-Type": "application/json"}
        self.base_url = '{}'.format(base_url)
        self.silent = silent
        self.delay = delay
        self._last_request_time = None
        if session:
            if not isinstance(session, requests.sessions.Session):
                raise TypeError('session must be requests.sessions.Session object.')
        else:
            if any([
                not (username or password),
                not (isinstance(username, basestring) or \
                    isinstance(password, basestring)),
                isinstance(username, basestring) and not username.strip(),
                isinstance(password, basestring) and not password.strip()
               ]):
                raise ValueError(('In the absense of session, expecting a valid '
                    ' non empty string, for both your username and password.'))
            session = requests.Session()
            session.auth = (username, password)
        self.session = session
        if not logger:
            logger = setup_logger()
        self.logger = logger
        
    def request(self, method, extension=None, params=None, headers=None,
                data=None, verify=False, **kwargs):
        """Requests a URL and returns a response.
        This method basically wraps the request method of the requests
        module.
        
        @type method: string
        @param method: The request method, e.g. 'get', 'post', etc.

        @type extension: string
        @param extension: (optional) The extension to append to the URL.
        
        @type params: string
        @param params: (optional) The URL query parameters

        @type headers: dict
        @param headers: (optional) Extra headers to sent with the request.
            Existing header keys can be overwritten.

        @type data: dict
        @param data: (optional) Dictionary

        @type verify: boolean
        @param verify: Option to verify host certs

        @type kwargs: dict
        @param kwargs: (optional) Arguments that will be passed to
            the `requests.request` method

        @rtype: dict
        @return: Return a dictionary which hold information about requested resource
        """
        url = '{}/{}'.format(self.base_url, extension)

        if headers:
            self.headers.update(headers)
        if data:
            data = json.dumps({'data':data})

        if self.delay > 0.0:
            t = time.time()
            if self._last_request_time is None:
                self._last_request_time = t
            elapsed = t - self._last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)

        request = self.session.request(method, url, params=params,
                                headers=self.headers, data=data, verify=verify,
                                **kwargs)
        self._last_request_time = time.time()
        if not self.silent:
            request.raise_for_status()
            
        return request.json() if request.text else {}
