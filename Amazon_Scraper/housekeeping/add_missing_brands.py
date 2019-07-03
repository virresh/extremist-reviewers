from pymongo import MongoClient

import json

mdb = MongoClient('192.168.2.212', 27017)

print("Connection Established")

products = mdb.amazon_brand_data.products
reviews = mdb.amazon_brand_data.reviews

print("Collections initialised")
tups = {}

y = products.aggregate(    
        [
            {"$group" : { "_id": "$asin", "brand":{'$first':"$brand"} } },
            {"$project": {"asin" : "$_id", "brand":1 ,"_id" : 1} },
        ]
    )

asin_to_brand = {}
for item in y:
    asin_to_brand[item["asin"]] = item["brand"]

z = reviews.find({"brand": {'$exists': False}}, {"asin":1, "id":1})

cnt=0
l = {}
for review in z:
    asin = review['asin']
    if asin_to_brand[asin]:
        l[asin] = asin_to_brand[asin]
        reviews.update({"id": review['id']}, {'$set': {'brand': asin_to_brand[asin]} })
        cnt+=1

print('done', cnt)
with open('x.dump', 'w') as f:
    json.dump(l, f, indent=4)
