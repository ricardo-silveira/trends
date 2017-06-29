# encoding: utf-8
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
from urllib import urlretrieve


def crawl(url, **kwargs):
    parser = kwargs.get("parser", "html.parser")
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    body_text = [x.text for x in soup.findAll("section")]
    return unicode("\n".join(body_text))


def get_img(body):
    img_url = ""
    img_filename = ""
    urlretrieve(img_url, img_filename)


if __name__ == "__main__":
    url_test = "http://www.eonline.com/news/863477/drake-brings-basketball-reporter-rosalyn-gold-onwude-as-his-date-to-the-2017-nba-awards"
    url_test = "http://www.eonline.com/news/863469/revenge-of-the-nerds-curtis-armstrong-tells-all-7-shocking-confessions-from-his-new-memoir"
    print crawl(url_test)
