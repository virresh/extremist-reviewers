from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import json

mdb = MongoClient('192.168.2.212', 27017)

print("Connection Established")

products = mdb.amazon_brand_data.reviews_test_test

products_new = mdb.amazon_brand_data.reviews_test

print("Collections initialised")
p = products.find({}, {"_id":0})

cnt = 0
for product in p:
    cnt+=1
    # print(product['asin'])
    if not list(products_new.find({"id":product['id']})):
        products_new.insert(product)
        print(product['asin'])
print(cnt)
