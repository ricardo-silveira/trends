import datetime
import os
import bbc
import g1
import eonline
import nytimes
import voiceuk
import cnn


class Spider(object):

    PARSERS = {"g1": g1.crawl,
               "bbc": bbc.crawl,
               "eonline": eonline.crawl,
               "cnn": cnn.crawl,
               "voiceuk": voiceuk.crawl,
               "nytimes": nytimes.crawl}
    DATA_URL = "data"

    def get_spider_name(self, url):
        url_terms = url.split(".")
        spider_name = url_terms[1]
        # special case for globo!
        if "glo.bo" in url:
            spider_name = "g1"
        return spider_name

    def parse(self, **kwargs):
        """
        Saves content to file
        """
        url = kwargs.get("url")
        spider_name = kwargs.get("spider", None)
        if not spider_name:
            spider_name = self.get_spider_name(url)
        try:
            content = self.PARSERS[spider_name](url)
            # creating directory structure
            now = datetime.datetime.now()
            dirs_list = [spider_name, now.year, now.month]
            output_path = self.DATA_URL
            for dir_name in dirs_list:
                output_path = "%s/%s" % (output_path, str(dir_name))
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
            # writing to file
            filename = url.split("/").pop()
            file_path = "%s/%s.txt" % (output_path, filename)
            with open(file_path, "wb+") as output:
                output.write(content.encode("utf-8"))
                return file_path
        except:
            return None
