"""
Crawler for Twitter data
module: twitter_crawler
author: Ricardo Silveira <ricardosilveira@poli.ufrj.br>
"""
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from dateutil import parser
import datetime
import requests
import logging
import json


LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename='cats_graph.log', level=logging.INFO)


class TwitterCrawler(object):
    """
    Crawler for Twitter data

    Methods
    -------
    get_user_lookup
    get_followers
    """

    def __init__(self, **kwargs):
        """
        Sets caller to connect to Twitter API

        Parameters
        ----------
        config: dict
            Settings for crawling twitter data, it must include the following:
        credential_queue: <Credential_Queue object>
            Object to make API calls and manage the credentials
        """
        self.__credential_queue = kwargs.get("credential_queue")
        self.__base_url = "https://api.twitter.com/1.1/"

    def __check_errors(self, data, api_call):
        """
        Checks if it is needed to repeat the request which returned `data`

        Parameters
        ----------
        data: dict
            Return of API request, must contain keys `header` and `data`
        api_call: str
            Label for request to update time window

        Returns
        -------
        (bool, bool)
            False, True: Request should not be repeated and its content is
                         not available.
            False, False: Request should not be repeated, but the data was
                          returned.
            True, False: Request must be repeated, and data is not available
        """
        # Connection error
        if not data["data"]:
            LOGGER.debug("Request failed!")
            return False, True
        # Successful request
        if "errors" not in data["data"] and "error" not in data["data"]:
            try:
                close_time = data["header"]['x-rate-limit-reset']
                self.__credential_queue.update_window(close_time, api_call)
                # Preventing error in next request
                if data["header"]['x-rate-limit-remaining'] == "0":
                    self.__credential_queue.next_credential(api_call)
            except KeyError:
                pass
            return False, False
        # Some error found
        if "errors" in data["data"] or "error" in data["data"]:
            # Credential reached limit
            if "errors" in data["data"] and data["data"]["errors"][0]["code"] == 88:
                close_time = data["header"]['x-rate-limit-reset']
                self.__credential_queue.update_window(close_time, api_call)
                self.__credential_queue.next_credential(api_call)
                return True, False
            # Account does not exist
            if "errors" in data["data"] and data["data"]["errors"][0]["code"] == 34:
                LOGGER.debug("Account does not exist")
        return False, True

    def get_user_lookup(self, **kwargs):
        """
        Collects information from user lookup call

        Parameters
        ----------
        screen_name: str
            Account screen name to collect data
        user_id: str
            Account id to collect data

        Returns
        -------
        dict
            All avaiable information regarding an account on Twitter
        """
        info = kwargs.get("screen_name", False)
        _attr = "screen_name"
        if not info:
            info = kwargs.get("user_id")
            _attr = "user_id"
        url = "%susers/lookup.json?%s=%s" % (self.__base_url, _attr, info)
        LOGGER.info("Requesting: %s" % url)
        api_call = "user_lookup"
        make_request = True
        print url
        while make_request:
            credential = self.__credential_queue.get(api_call)
            data = credential.request(url)
            make_request, found_error = self.__check_errors(data,
                                                            api_call)
        if not found_error:
            return data["data"][0]
        return None

    def get_followers(self, **kwargs):
        """
        Searches for all followers of a valid Twitter account

        Parameters
        ----------
        screen_name: str
            Account screen name to collect data
        user_id: str
            Account id to collect data

        Returns
        -------
        list
            List of ids of followers of an account
        """
        info = kwargs.get("screen_name", False)
        _attr = "screen_name"
        if not info:
            info = kwargs.get("user_id")
            _attr = "user_id"
        cursor = kwargs.get("cursor", None)
        api_call = "followers"
        followers_list = []
        errors_found = False
        # Whilre cursor is not pointing to the first page
        while not errors_found and cursor != "0":
            # Points to first page on first iteration
            url = "%sfollowers/ids.json?%s=%s" % (self.__base_url,
                                                  _attr,
                                                  info)
            if cursor:
                url = "%scursor=%s" % (url, cursor)
            credential = self.__credential_queue.get(api_call)
            data = credential.request(url)
            make_request, errors_found = self.__check_errors(data,
                                                             api_call)
            # If request returned valid data
            if not errors_found:
                cursor = data["data"]["next_cursor_str"]
                followers_list.extend(data["data"]["ids"])
        return followers_list

    def get_user_tweets(self, **kwargs):
        """
        Returns last `n` tweets from user specified by the `screen_name`

        Parameters
        ----------
        screen_name: str
            Account screen name to collect data
        user_id: str
            Account id to collect data
        n: int
            number of tweets to retrieve

        Returns
        -------
        list
            List of latest n tweets of an account
        """
        n = kwargs.get("n", 100)
        info = kwargs.get("screen_name", False)
        since_id = kwargs.get("since_id", None)
        _attr = "screen_name"
        if not info:
            info = kwargs.get("user_id")
            _attr = "user_id"
        api_call = "statuses"
        tweets_list = []
        url = "%s%s/user_timeline.json?%s=%s&count=%d" % (self.__base_url,
                                                          api_call,
                                                          _attr,
                                                          info,
                                                          n)
        if since_id:
            url = "%s&since_id=%s" % (url, str(since_id))
        credential = self.__credential_queue.get(api_call)
        data = credential.request(url)
        make_request, errors_found = self.__check_errors(data,
                                                         api_call)
        if not errors_found:
            # If request returned valid data
            for tweet in data["data"]:
                # retrieving relevant info from tweet
                try:
                    t_dict = {}
                    t_dict["url"] = tweet["entities"]["urls"][0]["expanded_url"]
                    t_dict["id"] = tweet["id"]
                    t_dict["likes_count"] = tweet["favorite_count"]
                    t_dict["shares_count"] = tweet["retweet_count"]
                    t_dict["created_at"] = parser.parse(tweet["created_at"]).isoformat()
                    t_dict["collected_at"] = datetime.datetime.utcnow().isoformat()
                    tweets_list.append(t_dict)
                except IndexError:
                    pass
        return tweets_list

    def get_tweet_info(self, **kwargs):
        """
        Parameters
        ----------
        tweet_id: str
            id for tweet to monitor
        """
        tweet_id = kwargs.get("tweet_id")
        api_call = "statuses"
        url = "%s%s/show.json?id=%s" % (self.__base_url,
                                        api_call,
                                        tweet_id)
        credential = self.__credential_queue.get(api_call)
        data = credential.request(url)
        make_request, errors_found = self.__check_errors(data,
                                                         api_call)
        if not errors_found:
            # If request returned valid data
            likes_count = data["data"]["favorite_count"]
            shares_count = data["data"]["retweet_count"]
            checked_at = datetime.datetime.utcnow().isoformat()
        stats = {}
        stats["likes_count"] = likes_count
        stats["shares_count"] = shares_count
        stats["checked_at"] = checked_at
        return stats


if __name__ == "__main__":
    CONFIG = {"config_credentials_path": "credentials.json",
              "verification_url":  "https://api.twitter.com/1.1/users/" +
              "lookup.json?screen_name=twitterapi,twitter"}
    #from credential_queue import CredentialQueue
    #CREDENTIAL_QUEUE = CredentialQueue(config=CONFIG, request_limit=10)
    #CRAWLER = TwitterCrawler(credential_queue=CREDENTIAL_QUEUE)
    #monitor_list = {"bbc": [],
    #                "cnn": [],
    #                "g1": [],
    #                "enews": [],
    #                "thevoicenews": [],
    #                "nytimes": []}
    #print CRAWLER.get_tweet_info(tweet_id="879543064494301184")
    #for screen_name in monitor_list.keys():
    #    monitor_list[screen_name] = CRAWLER.get_user_tweets(screen_name=screen_name)
    #with open("tmp_tweets.json", "wb+") as out:
    #    json.dump(monitor_list, out)
