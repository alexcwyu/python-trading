import pymongo
import datetime


from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.test_database
collection = db.test_collection
post = {"author": "Mike",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}

posts = db.posts
post_id = posts.insert_one(post).inserted_id

print post_id

print posts.find_one()

print posts.find_one({"author": "Mike"})

print posts.find_one({"_id": post_id})
