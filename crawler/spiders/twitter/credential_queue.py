"""
Selects valid credential to connect to the API
module: credential_queue
author: Ricardo Silveira <ricardosilveira@poli.ufrj.br>
"""
import json
import time
import logging

from auth_user import AuthUser

LOGGER = logging.getLogger(__name__)
INF = float("inf")


class CredentialQueue(object):
    """
    Manages credential to connect to the API

    Atributes
    ---------
    request_limit: int
        Limit for `Auth_User` object to define timeout exception
    config: dict
        Json decoded data with settings for the API

    Methods
    -------
    get
        Returns an authenticated and available credential to request data
    """

    def __init__(self, **kwargs):
        """
        Loads credentials when instanced and sets default attriutes

        Parameters
        ----------
        config: dict
            Settings to authenticate an user. It must have the following items:
                config_credentials_path: path to json file storing credentials,
                                         it must follow the layout
                                         [{"a":
                                             {"Consumer Key (API Key)": .,
                                              "Consumer Secret (API Secret)": .
                                              "Access Token": .,
                                              "Access Token Secret": .}}]
                verification_url: url to verify if the credential is valid
        request_limit: int
            Number of requests attempts before dropping request

        Raises
        ------
        ValueError Exception:
            If no valid credentials are available to connect to the API
        """
        self.request_limit = kwargs.get("request_limit", 10)
        self.config = kwargs.get("config")
        self.__credential_index = 0
        self.__close_time = []
        self.__cursor = -1
        self.__credentials = self.__load_credentials()
        if not self.__credentials:
            raise ValueError("Error: No valid credentials available!")

    def __load_credentials(self):
        """
        Loads valid credentials for API

        Returns
        -------
        list
            List of valid authenticated users to request data to the API
        bool
            False if no credentials available
        """
        LOGGER.info('Loading credentials...')
        config = self.config
        credentials_json = json.load(open(config["config_credentials_path"]))
        credentials = []
        for user in credentials_json:
            label = user.keys().pop()
            LOGGER.info("Authenticating %s" % label)
            consumer_key = user[label]["Consumer Key (API Key)"]
            consumer_secret = user[label]["Consumer Secret (API Secret)"]
            token_key = user[label]["Access Token"]
            token_secret = user[label]["Access Token Secret"]
            credential = AuthUser(label=label,
                                   request_limit=self.request_limit,
                                   consumer_key=consumer_key,
                                   consumer_secret=consumer_secret,
                                   token_key=token_key,
                                   token_secret=token_secret)
            try:
                data = credential.request(config["verification_url"])
                if data["data"] is not False:
                    if data["header"]["status"] == '200':
                        credentials.append(credential)
                        self.__close_time.append({"user_lookup": INF,
                                                  "followers": INF,
                                                  "statuses": INF})
                        LOGGER.info("Authentication succeed!")
                    else:
                        LOGGER.info("Authentication failed")
            except:
                LOGGER.debug("An exception was raised!", exc_info=1)
        if len(credentials) < 1:
            return False
        LOGGER.info("%d credentials loaded" % len(credentials))
        return credentials

    def next_credential(self, api_call):
        """
        Sets time limit for current credential and points the list index for
        the next available one. If none is available, then sets a wait-state

        Parameters
        ----------
        api_call: str
            key for close_time dictionary mapping time limit for the request
        """
        LOGGER.info("Credential: %d/%d" % (self.__credential_index+1,
                                           len(self.__credentials)))
        start_point = self.__credential_index
        available = False
        while not available:
            # Circular pythonic reference to the last credential
            if self.__credential_index + 1 == len(self.__credentials):
                self.__credential_index = -1
            self.__credential_index += 1
            now = int(time.time())
            time_window = self.__close_time[self.__credential_index][api_call]
            time_remaining = time_window - now
            if time_remaining > 0:
                available = True
            else:
                if self.__credential_index == start_point:
                    time.sleep(abs(time_remaining))

    def get(self, api_call):
        """
        Selects valid credential for the specific api all, if current is not
        available, then jumps to the next possible credential.

        Parameters
        ----------
        api_call: str
            key for close_time dictionary mapping time limit for the request

        Returns
        -------
        OAuth2.client
            authenticated client for http requests

        Examples
        --------
        Basic usage

        >>> credential = get_available_credential("followers")
        """
        time_window = self.__close_time[self.__credential_index][api_call]
        now = int(time.time())
        # Reached limit for this `api_call`
        if now > time_window and time_window:
            self.next_credential(api_call)
        return self.__credentials[self.__credential_index]

    def update_window(self, close_time, api_call):
        """
        Updates time limit for credential to reach limit for the specified
        api call
        """
        self.__close_time[self.__credential_index][api_call] = int(close_time)

if __name__ == "__main__":
    CONFIG = {"config_credentials_path": "../../config/credentials.json",
              "verification_url": "https://api.twitter.com/1.1/" +
                                  "account/verify_credentials.json"}
    MANAGER = CredentialQueue(config=CONFIG, request_limit=10)
