from flask import Flask, render_template
import os

# Подгружение переменных окружения
# Файл /.env
from dotenv import load_dotenv
load_dotenv()

from addons import MongoDBWorker
from addons import WebCrawler

MONGODB_USERNAME = os.environ["MONGODB_USERNAME"]
MONGODB_PASSWORD = os.environ["MONGODB_PASSWORD"]
MONGODB_DBNAME = os.environ["MONGODB_DBNAME"]

app = Flask(__name__)
# from addons.dclasses import Category
# import dataclasses

# def main():
#     mdbworker = MongoDBWorker("parser_admin", "parser", "v102parserdb")
#     # mdbworker.add_category(Category(title="Происшествия", index=185, path="/accidents"))
#     # wc = WebCrawler(mdbworker.get_categories())
#     # print(mdbworker.get_categories())
#     import pprint
#     pprint.pprint([dataclasses.asdict(x) for x in mdbworker.get_categories()])
#     # from pprint import pprint
#     # for v in wc.crawl(stopittervalue=3):
#     #     for c in v:
#     #         pprint(dataclasses.asdict(c))

# if __name__ == "__main__":
#     main()

def start_crawler(cats, mdbworker):
    wc = WebCrawler(cats)
    from pprint import pprint
    for v in wc.crawl(stopittervalue=3):
        mdbworker.add_articles(v)

@app.route('/')
def index():
    mdbworker = MongoDBWorker(MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_DBNAME)
    cats = mdbworker.get_categories()

    # start_crawler(cats, mdbworker)
    arts = mdbworker.get_articles(40, 0)

    return render_template("index.html", categories=cats, articles=arts)

if __name__ == "__main__":
    app.run(threaded=True, port=5000)