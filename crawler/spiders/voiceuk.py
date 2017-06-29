# encoding: utf-8
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
from urllib import urlretrieve


def crawl(url, **kwargs):
    parser = kwargs.get("parser", "html.parser")
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    body_text = [x.text for x in soup.findAll("p")]
    return unicode("\n".join(body_text))


def get_img(body):
    img_url = ""
    img_filename = ""
    urlretrieve(img_url, img_filename)


if __name__ == "__main__":
    url_test = "http://www.voice-online.co.uk/article/memorial-unveiled-black-soldiers-who-fought-britain"
    url_test = "http://www.voice-online.co.uk/article/recruiters-warned-dangers-work-relationships"
    print crawl(url_test)
