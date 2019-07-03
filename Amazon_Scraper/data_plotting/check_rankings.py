from pymongo import MongoClient
import pandas as pd
import sys

mdb = MongoClient('192.168.2.212', 27017)
reviewers_db = mdb.amazon_brand_data.reviewers_test
df = pd.read_csv('params_new.csv', sep=';')

cntr=0
# for i in df['reviewer_id']:
res = reviewers_db.find({'id': {'$in': list(df['reviewer_id'])}})
print('rank', 'author_id', sep=';')
for k in res:
	print(k['rank'], k['id'], sep=';')
