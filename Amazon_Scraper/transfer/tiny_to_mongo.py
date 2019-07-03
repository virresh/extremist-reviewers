from tinydb import TinyDB, Query
from pymongo import MongoClient

mdb = MongoClient('192.168.2.212', 27017)

tdb = TinyDB('../products.json')
products = mdb.amazon_brand_data.products

res = products.insert_many(tdb.all())
print(res)


tdb2 = TinyDB('../reviews.json')
products = mdb.amazon_brand_data.reviews

res = products.insert_many(tdb.all())
print(res)
