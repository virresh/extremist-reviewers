from pymongo import MongoClient

import json


mdb = MongoClient('192.168.2.212', 27017)

print("Connection Established")

reviews = mdb.amazon_brand_data.reviews_test

print("Collections initialised")

res = reviews.aggregate(
        [
            {
                "$group" : { 
                   "_id": {
                        "brand":"$brand", 
                        "aid":"$author_id"
                   },
                   "count": {"$sum": 1},
                   "verified": {"$sum": {"$cond": ["$verified_purchase",1,0] } },
                   "not_verified": {"$sum": {"$cond": ["$verified_purchase",0,1] } }
                   # "entry":{
                   #      "$push":{
                   #          "review_text":"$text",
                   #          "asin":"$asin"
                   #      }
                   #  }
                } 
            },
            {
            	"$sort":{
            		"count":-1
            	}
            }
        ], allowDiskUse=True
)

# for entry in res:
# 	print(entry['_id']['brand'], entry['_id']['aid'], entry['count'])
with open('coupling.txt', 'w') as f:
	for entry in res:
		# f.write(entry['_id']['aid'] + "@" + str(entry['_id']['brand']) + "@" + str(entry['count']) + "@" + str(entry['verified']) + "@" + str(entry['not_verified']) + "\n")
		f.write(entry['_id']['aid'] + ";" + str(entry['_id']['brand']) + ";" + str(entry['count']) + ";" + str(entry['verified']) + ";" + str(entry['not_verified']) + "\n")
