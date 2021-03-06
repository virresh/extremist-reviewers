import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import matplotlib
matplotlib.use('Agg')

from pymongo import MongoClient
from datetime import date
from statistics import median
import pandas as pd
import sys
import re
import math
from collections import Counter
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import spatial

# # Reference: https://stackoverflow.com/questions/15173225/calculate-cosine-similarity-given-2-sentence-strings/15173821
# WORD = re.compile(r'\w+')
# def get_cosine(vec1, vec2):
# 	intersection = set(vec1.keys()) & set(vec2.keys())
# 	numerator = sum([vec1[x] * vec2[x] for x in intersection])
# 	sum1 = sum([vec1[x]**2 for x in vec1.keys()])
# 	sum2 = sum([vec2[x]**2 for x in vec2.keys()])
# 	denominator = math.sqrt(sum1) * math.sqrt(sum2)
# 	return float(numerator) / denominator if denominator else 0.0
# def text_to_vector(text):
# 	words = WORD.findall(text)
# 	return Counter(words)

mdb = MongoClient('192.168.2.212', 27017)
reviews_all = mdb.amazon_brand_data.reviews_test_test
result = reviews_all.find({}, {"author_id":1, "text":1, "rating":1,"_id":0})

reviewers = {}

with tf.device('/device:CPU:0'):
    embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder/1")

tf.logging.set_verbosity(tf.logging.ERROR)

names = []
review_text = []
rating_sum = {}
rating_count = {}

for c,i in enumerate(list(result)):
	#if c>=1000: break
	names.append(i['author_id'])
	review_text.append(i['text'])
	rating = float(i['rating'])
	try:
		rating_sum[i['author_id']] += rating
		rating_count[i['author_id']] += 1
	except:
		rating_sum[i['author_id']] = rating
		rating_count[i['author_id']] = 1
        
embedded_text = np.empty([])

print("Fetched",len(review_text),"reviews.")

WINDOW_SIZE = 32700
for i in range(0,len(review_text),WINDOW_SIZE):
	print("Processed",i,"reviews")
	with tf.Session() as session:
		session.run([tf.global_variables_initializer(), tf.tables_initializer()])
		message_embeddings = session.run(embed(review_text[i:min(len(review_text),i+WINDOW_SIZE)]))
		if i==0: embedded_text = np.array(message_embeddings)
		else: embedded_text = np.append(embedded_text, np.array(message_embeddings), axis = 0)
    
print(np.shape(embedded_text))
print("Done with embeddings.")

for i in range(len(embedded_text)):
	to_append = embedded_text[i]
	try: reviewers[names[i]].append(to_append)
	except: reviewers[names[i]] = [to_append]

# df = pd.read_csv('data/params.csv', sep=';')
# classes = {}
# for i,row in df.iterrows():
# 	if row['avg_rating'] >= 4:
# 		classes[row['reviewer_id']] = 1
# 	elif row['avg_rating'] <= 2:
# 		classes[row['reviewer_id']] = -1
# 	else:
# 		classes[row['reviewer_id']] = 0

lovers = []
haters = []
others = []
tmp = []
not_found = 0

cosines = {}

print("Total:",sum([len(i) for i in reviewers.values()]))

for now,author in enumerate(reviewers.keys()):
	if now%100==0: print(now,len(reviewers))
	if(len(reviewers[author])) < 2: continue
	for i in range(len(reviewers[author])):
		for j in range(i+1,len(reviewers[author])):
			cos = abs(1-spatial.distance.cosine(reviewers[author][i], reviewers[author][j]))
			try: cosines[author].append(cos)
			except: cosines[author] = [cos]

	cosines[author] = median(cosines[author])
	try:
		if rating_sum[author]/rating_count[author] >= 4:
			lovers.append({'reviewer_id':author, 'median_cosine':cosines[author]})
		elif rating_sum[author]/rating_count[author] <= 2:
			haters.append({'reviewer_id':author, 'median_cosine':cosines[author]})
		else:
			others.append({'reviewer_id':author, 'median_cosine':cosines[author]})
	except:
		not_found += 1

print("Not found errors:",not_found)
lovers = pd.DataFrame(lovers)
haters = pd.DataFrame(haters)
others = pd.DataFrame(others)

all = lovers
all.append(haters)
all.append(others)

params = pd.read_csv('./data/params.csv', sep=';')
all = pd.merge(params,all, on='reviewer_id')
all.to_csv('params_new.csv',sep=';')

fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters['median_cosine'].hist(density=True, color='r', alpha=0.5, ax=ax0)
ax0.set_title('Brand Haters')
lovers['median_cosine'].hist(density=True, color='g', alpha=0.5, ax=ax1)
ax1.set_title('Brand Lovers')
others['median_cosine'].hist(density=True, color='b', alpha=0.5, ax=ax2)
ax2.set_title('Others')
haters['median_cosine'].hist(density=True, color='r', alpha=0.5, ax=ax3)
lovers['median_cosine'].hist(density=True, color='g', alpha=0.5, ax=ax3)
others['median_cosine'].hist(density=True, color='b', alpha=0.5, ax=ax3)

ax3.set_title('All')
plt.suptitle('Median cosine similarity of reviewers')
plt.savefig("cosine_similarity.png")
plt.show()
