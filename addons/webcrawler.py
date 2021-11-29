from .dclasses import Article
from bs4 import BeautifulSoup
from multiprocessing import Pool
from datetime import datetime
from dateutil.parser import isoparse
from functools import partial
import time
import requests
import re

class LackOfPages(Exception):
    pass

class WebCrawler:
    def __init__(self, categories, pool_length=10):
        self.categories = categories
        self.pool_length = pool_length
        self.baseURL = "https://www.volzsky.ru"

    def __get_url_markdown(self, url, params={}):
        markdown = requests.get(url, params=params)

        if not markdown.text or markdown.text.isspace():
            raise LackOfPages

        time.sleep(1)

        return markdown.text

    # page_type
    # 0 - cat
    # 1 - art
    def __get_page(self, category_index, page_index):
        page_url = "https://www.volzsky.ru/index.php"
        
        page_params = {
            "categ": category_index,
            "st": page_index
        }

        # page_params = {
        #     "wx2": page_index
        # }

        # if (page_index == 1):
        #     page_url = self.baseURL + f"/index.php?wx=16&categ={category_index}"
        #     page_params = {}

        return self.__get_url_markdown(page_url, params=page_params)

    def __gen_article_object(self, article_url, category_title):
        article_markdown = self.__get_url_markdown(article_url)
        article_soup = BeautifulSoup(article_markdown, "html.parser")

        date_raw = article_soup.select_one("meta[itemprop='datePublished']")["content"]
        title_raw = article_soup.select_one("h1#title_news").get_text(strip=True)

        comments_count_raw = article_soup.select("div#commetnprint > div")
        if len(comments_count_raw) == 0:
            comments_count_raw = 0
        else:
            comments_str = comments_count_raw[0].get_text(strip=True)
            comments_count_raw = re.search(r"\d+", comments_str).group(0)

        text_raw_wrapper = article_soup.new_tag("div")
        text_raw = article_soup.select("div#bt_center p")
        for p in text_raw:
            text_raw_wrapper.append(p)
        text_raw = text_raw_wrapper

        main_photo_raw = article_soup.select_one("div#mainfoto img")["src"]
        main_photo_link = self.baseURL + "/" + main_photo_raw
        # main_photo_link = re.search(r"(?<=url\().*(?=\))", main_photo_raw).group(0)

        # photos_raw = article_soup.select("div.n-text img")
        # photos_links = [x["src"] for x in photos_raw]
        photos_links = []
        videos_links = []

        # videos_raw = article_soup.select("div.n-text iframe")
        # videos_links = [x["src"] for x in videos_raw]

        return Article(
            date            =   isoparse(date_raw), # Преобразуем дату в виде строки в Datetime
            link            =   article_url,
            title           =   title_raw,
            category        =   category_title,
            comments_count  =   int(comments_count_raw),
            text            =   text_raw.get_text(),
            photos          =   [main_photo_link] + photos_links,
            videos          =   videos_links
        )

    def get_news_from_page(self, category, current_page_index):
        try:
            news_page_markdown = self.__get_page(category_index=category["index"], page_index=current_page_index)
        except LackOfPages:
            print("No pages left")
        except StopIteration:
            print("На сайте нет такой категории, либо введены некорректные данные")

        news_soup = BeautifulSoup(news_page_markdown, "html.parser")
        articles_links_raw = news_soup.select("""div.btc_h a""")
        articles_links = [self.baseURL + "/" + x["href"] for x in articles_links_raw]

        articles = []

        for a in articles_links[:8]:
            articles.append(self.__gen_article_object(a, category_title=category["title"]))

        return articles

    def crawl(self, stopittervalue=-1):
        for cat in self.categories:
            current_page_index = 0
            while current_page_index < stopittervalue:
                print(f"Crawl in {cat['path']} at {current_page_index}")
                yield self.get_news_from_page(cat, current_page_index)

                current_page_index += 1

    # def crawl(self, stopittervalue=-1):
    #     for cat in self.categories:
    #         current_page_index = 1
    #         while current_page_index < stopittervalue or stopittervalue == -1:
    #             print(f"Crawl in {cat['path']} at {current_page_index}")
    #             l = self.pool_length
    #             if stopittervalue != -1 and current_page_index + self.pool_length >= stopittervalue:
    #                 l = stopittervalue - current_page_index
                
    #             pages_indexes = [current_page_index + i for i in range(l)] #iterable
    #             get_news_func = partial(self.get_news_from_page, cat)
    #             with Pool(l) as p:
    #                 res_arr = p.map(get_news_func, pages_indexes) # Получаем массив ответов, длинна которого равна pages_indexes
    #                 for r in res_arr:
    #                     yield r # возвращаем массив статей на странице

    #             current_page_index += l