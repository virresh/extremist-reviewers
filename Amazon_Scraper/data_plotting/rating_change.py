from pymongo import MongoClient
from datetime import date
import pandas as pd
import sys
import matplotlib.pyplot as plt

mdb = MongoClient('192.168.2.212', 27017)
reviews_all = mdb.amazon_brand_data.reviews_test_test
reviewers_all = mdb.amazon_brand_data.reviewers_test
all_reviews = {}
result = reviews_all.find({}, {"asin":1, "date":1, "rating":1, "author_id":1, "_id":0})
all_reviewers = reviewers_all.find({}, {"asin":1, "date":1, "_id":0})
for review in list(result):
	r_date = date(review['date'][0],review['date'][1],review['date'][2])
	try:
		all_reviews[review['asin']].append((r_date,review['rating'], review['author_id']))
	except:
		all_reviews[review['asin']] = [(r_date,review['rating'], review['author_id'])]

df = pd.read_csv('data/params.csv', sep=';')
classes = {}
# for i,row in df.iterrows():
# 	if row['avg_rating'] >= 4:
# 		classes[row['reviewer_id']] = 1
# 	elif row['avg_rating'] <= 2:
# 		classes[row['reviewer_id']] = -1
# 	else:
# 		classes[row['reviewer_id']] = 0

# lovers = []
# haters = []
# others = []
all_classes = []
tmp = []
not_found = 0

WINDOW_SIZE = 5
for k in all_reviews.keys():
	for i in range(len(all_reviews[k])):
		before = [x[1] for x in all_reviews[k][max(0,i-WINDOW_SIZE):i]]
		after = [x[1] for x in all_reviews[k][i:min(len(all_reviews[k]),i+WINDOW_SIZE)]]
		if len(before) and len(after):
			delta = sum(after)/len(after) - sum(before)/len(before)
			#print(delta)
			try:
				all_classes.append({'reviewer_id':all_reviews[k][i][2], 'avg_change':delta})
				# if classes[all_reviews[k][i][2]] == 1:
				# 	lovers.append({'reviewer_id':all_reviews[k][i][2], 'avg_change':delta})
				# elif classes[all_reviews[k][i][2]] == -1:
				# 	haters.append({'reviewer_id':all_reviews[k][i][2], 'avg_change':delta})
				# else:
				# 	others.append({'reviewer_id':all_reviews[k][i][2], 'avg_change':delta})
			except:
				not_found += 1

print("Not found errors:",not_found)
all_df = pd.DataFrame(all_classes)
# lovers = pd.DataFrame(lovers)
# haters = pd.DataFrame(haters)
# others = pd.DataFrame(others)
all_df.to_csv('data/rating_changes.txt', sep=';', index=None)
