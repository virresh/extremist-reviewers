from pymongo import MongoClient

# import json
import requests as req
import time

mdb = MongoClient('192.168.2.212', 27017)

print("Connection Established")

reviews = mdb.amazon_brand_data.reviews_test_test
r2 = mdb.amazon_brand_data.reviews_test

print("Collections initialised")

z = r2.find({'exists': False}, {"asin":1, "id":1, "review_url":1}, no_cursor_timeout=True)

counter = 0
for review in z:
    counter += 1
    reviews.update_one({"id": review['id']}, {"$set": {"exists": False}})
print('Completed - ', counter)
z.close()
