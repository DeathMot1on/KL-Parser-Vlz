from .dclasses import Article
from .dclasses import Category
import dataclasses
import pymongo

class MongoDBWorker:
    def __init__(self, username, password, dbname):
        self.username = username
        self.password = password
        self.dbname = dbname
        self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@volzskydataclaster.zytfj.mongodb.net/{dbname}?tls=true&tlsAllowInvalidCertificates=true&retryWrites=true&w=majority")
        self.db = self.client[dbname]

    def add_category(self, category):
        category_id = self.db["categories"].insert_one(dataclasses.asdict(category)).inserted_id
        print(f"Inserted with ID: {category_id}")

    def get_categories(self):
        res = []
        for c in self.db["categories"].find({}):
            res.append(Category(title=c["title"], index=c["index"], path=c["path"]))
        return res

    def add_articles(self, articles):
        inserted_ids = self.db["articles"].insert_many([dataclasses.asdict(x) for x in articles]).inserted_ids
        for i in inserted_ids:
            print(f"Inserted article with ID: {i}")

    def get_articles(self, l, offset):
        res = []
        for a in self.db["articles"].find({}).skip(offset).limit(l):
            res.append(Article(
                title=a["title"],
                category=a["category"],
                date=a["date"],
                link=a["link"],
                text=a["text"],
                videos=a["videos"],
                photos=a["photos"],
                comments_count=a["comments_count"]
            ))
        return res

    # def get_categories(self):
    #     categories = {
    #         194: "/politics",
    #         184: "/investigation",
    #         185: "/accidents",
    #         195: "/econom",
    #         196: "/society",
    #         198: "/sport",
    #         201: "/telecom",
    #         214: "/corruption",
    #         227: "/ecology",
    #         228: "/zdravoohranenie"
    #     }
    #     return [Category(title="", index=k, path=v) for k,v in categories.items()]
