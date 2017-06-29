# encoding: utf-8
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
from urllib import urlretrieve


def crawl(url, **kwargs):
    parser = kwargs.get("parser", "html.parser")
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    body_text = [x.text for x in soup.findAll("p", class_="content-text__container")]
    return unicode("\n".join(body_text))


def get_img(body):
    img_url = ""
    img_filename = ""
    urlretrieve(img_url, img_filename)

if __name__ == "__main__":
    url_test = "http://www.bbc.co.uk/earth/story/20170515-the-animals-that-look-helpless-but-are-secretly-fearsome?ns_mchannel=social&ns_source=masterbrand_twitter&ns_campaign=pan_bbc_220517&ns_linkname=image_link&ns_fee=0"
    print crawl(url_test)
