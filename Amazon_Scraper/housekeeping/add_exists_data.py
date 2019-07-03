from pymongo import MongoClient

# import json
import requests as req
import time

mdb = MongoClient('192.168.2.212', 27017)

print("Connection Established")

reviews = mdb.amazon_brand_data.reviews_test_test
r2 = mdb.amazon_brand_data.reviews_test

print("Collections initialised")

z = reviews.find({'exists': True}, {"asin":1, "id":1, "review_url":1}, no_cursor_timeout=True)

counter = 0
for review in z:
    counter += 1
    # print(review)
    r = req.get(review['review_url'])
    if r.status_code == 404:
        r2.update_one({"id": review['id']}, {"$set": {"exists": False}})
        print('Updated ', review['id'], 'to', r.status_code)
        reviews.update_one({"id": review['id']}, {"$set": {"exists": False}})
    elif r.status_code == 503:
        print('Waiting_on', review['id'], counter)
        time.sleep(1)
    elif r.status_code != 200:
        print('Unknown', review['id'], r.status_code)
print('Completed - ', counter)
z.close()
