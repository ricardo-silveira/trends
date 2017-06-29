"""
Authenticates valid credential and performs http requests
module: auth_user
author: Ricardo Silveira <ricardosilveira@poli.ufrj.br>
"""
import oauth2 as oauth
import logging
import json

from str_tool import clean_str

LOGGER = logging.getLogger(__name__)


class AuthUser(object):
    """
    Authenticated user to perform http requests

    Attributes
    ----------
    label: str
        Label for identifying requester
    request_limit: int
        Limit for repeating a request until droping it

    Methods
    -------
    request(url)
        Same as request.get(url) for authenticated credential
    """

    def __init__(self, label, **kwargs):
        """
        Sets valid requester for http calls

        Parameters
        ------------
        label: str
            Label for object
        request_limit: int
            Request counter limit (default '10')
        consumer_key: str
            Key for instancing a Consumer object
        consumer_secret: str
            Secret for instancing a Consumer object
        token_key: str
            Key for instancing a Token object
        token_secret: str
            Secret for instancing a Token object

        Examples
        --------
        Basic usage:
        >>> auth_user("test_user",
                      request_limit=10,
                      consumer_key="HAdui423",
                      consumer_secret="9sdafh2"
                      token_key="4293dE",
                      token_secret="24dsadf4")
        """
        self.label = label
        self.request_limit = kwargs.get("request_limit", 10)
        self.__consumer_key = clean_str(kwargs.get("consumer_key"))
        self.__consumer_secret = clean_str(kwargs.get("consumer_secret"))
        self.__token_key = clean_str(kwargs.get("token_key"))
        self.__token_secret = clean_str(kwargs.get("token_secret"))
        self.requester = self.__log_in()

    def __log_in(self):
        """
        Authenticates user and returns client object to perform requests

        Returns
        -------
        oauth.Consumer object
            Authenticated requester
        """
        try:
            consumer = oauth.Consumer(key=self.__consumer_key,
                                      secret=self.__consumer_secret)
            access_token = oauth.Token(key=self.__token_key,
                                       secret=self.__token_secret)
            return oauth.Client(consumer, access_token)
        except Exception, traceback:
            LOGGER.error(traceback)

    def request(self, url):
        """
        Requests data from `url`.

        Parameters
        ----------
        url: str
            url for request to be executed

        Returns
        -------
        dict
            Dictionary containing header and data from the requested `url`,
            following the structure: {"data": data, "header": header}
            If it reaches the `request_limit`, data and header = False.

        Examples
        --------
        Basic use

        >>> request("http://google.com")
        {"data": [{...}], "header": {...}}
        """
        LOGGER.debug("Requesting: %s" % url)
        for call_counter in xrange(self.request_limit):
            try:
                header, data = self.requester.request(url)
                return {"data": json.loads(data), "header": header}
            except Exception, error_msg:
                LOGGER.debug(error_msg, exc_info=True)
                pass
        LOGGER.error("Connection error")
        return {"data": False, "header": False}
