# encoding: utf-8
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
from urllib import urlretrieve


def crawl(url, **kwargs):
    parser = kwargs.get("parser", "html.parser")
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    body_text = [x.text for x in soup.findAll("div", class_="pg-rail-tall__body")]
    return unicode("\n".join(body_text))


def get_img(body):
    img_url = ""
    img_filename = ""
    urlretrieve(img_url, img_filename)


if __name__ == "__main__":
    url_test = "http://edition.cnn.com/2017/06/26/us/iraqi-deportation-stay-michigan/index.html?sr=twCNN062717iraqi-deportation-stay-michigan0255AMVODtopLink&linkId=39133456"
    print crawl(url_test)
