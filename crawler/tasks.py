from ast import literal_eval
import redis
import json
from celery.task import task
from crawler.spiders.twitter.crawler import TwitterCrawler
from crawler.spiders.twitter.credential_queue import CredentialQueue
from trend.models import Source, Article, Tweet, Stat, Term
from subprocess import call
from crawler.spiders.spider import Spider
from datetime import datetime, timedelta


LIST_NAME = "url_list"


@task()
def monitor_accounts(*args, **kwargs):
    print "=======MONITORING ACCOUNTS=======\n\n"
    accounts_list = kwargs.get("accounts_list")
    CONFIG = {"config_credentials_path": "credentials.json",
              "verification_url":  "https://api.twitter.com/1.1/users/" +
              "lookup.json?screen_name=twitterapi,twitter"}
    CREDENTIAL_QUEUE = CredentialQueue(config=CONFIG, request_limit=10)
    CRAWLER = TwitterCrawler(credential_queue=CREDENTIAL_QUEUE)
    monitor_list = {}
    for screen_name in accounts_list:
        # Loading source and settings
        source, check = Source.objects.get_or_create(screen_name=screen_name,
                                                     name=screen_name,
                                                     web_url='')
        # Retrieving last tweet for account
        since_id = None
        try:
            since_id = Tweet.objects.filter(source=source).latest('created_at')
        except:
            pass
        monitor_list[screen_name] = CRAWLER.get_user_tweets(screen_name=screen_name,
                                                            since_id=since_id)
    # in theory, going for new tweets
    r = redis.Redis(host='localhost', port=6379, db=0, password="bigdata2017")
    for screen_name, tweets_list in monitor_list.iteritems():
        source = Source.objects.filter(screen_name=screen_name)[0]
        for tweet in tweets_list:
            url = tweet["url"]
            article = Article()
            tweet_obj = Tweet()
            tweet_obj.id = tweet["id"]
            tweet_obj.created_at = tweet["created_at"]
            tweet_obj.source = source
            tweet_obj.save()
            print tweet, tweet_obj
            r.lpush(LIST_NAME, (screen_name, url))


@task()
def monitor_tweets(*arg, **kwargs):
    print "=======MONITORING TWEETS=======\n\n"
    CONFIG = {"config_credentials_path": "credentials.json",
              "verification_url":  "https://api.twitter.com/1.1/users/" +
              "lookup.json?screen_name=twitterapi,twitter"}
    CREDENTIAL_QUEUE = CredentialQueue(config=CONFIG, request_limit=10)
    CRAWLER = TwitterCrawler(credential_queue=CREDENTIAL_QUEUE)
    time_threshold = datetime.now() - timedelta(hours=6)
    tweets_to_monitor = Tweet.objects.filter(created_at__gt=time_threshold)
    for tweet in tweets_to_monitor:
        tweet_stats = CRAWLER.get_tweet_info(tweet_id=str(tweet.id))
        stat = Stat();
        stat.tweet = tweet
        stat.likes_count = tweet_stats["likes_count"]
        stat.shares_count = tweet_stats["shares_count"]
        stat.save()
        print tweet_stats, stat


@task()
def extract_terms(*args, **kwargs):
    """
    Calling spark process to compute tfidf
    """
    print "=======EXTRACTING TERMS=======\n\n"
    input_path = kwargs.get("input_path", "data/g1/2017/6")
    output_path = kwargs.get("output_path", "tmp.json")
    source_name = "g1"
    if input_path and output_path:
        call(["spark-submit",
              "extract_relevant_terms.py",
              input_path,
              output_path])
        tfidf_output = json.load(open(output_path))
        for item in tfidf_output:
            article = Article.objects.filter(file_path=item['doc'], extracted=0)
            if article:
                source = Source.objects.get(name=source_name)
                article.extracted = 1
                article.file_path = item["doc"]
                article.save()
                term = Term()
                term.score = item["score"]
                term.text = item["term"]
                term.article = article
                term.save()
                print term, item


@task()
def crawl_news(*args, **kwargs):
    print "=======CRAWL NEWS=======\n\n"
    r = redis.Redis(host='localhost',
                    port=6379,
                    db=0,
                    password="bigdata2017")
    parse_news = True
    while parse_news:
        item = r.lpop(LIST_NAME)
        if not item:
            parse_news = False
        else:
            screen_name, url = literal_eval(item)
            spider = Spider()
            print spider.parse(spider=screen_name, url=url)
