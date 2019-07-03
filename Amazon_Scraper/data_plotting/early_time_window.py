from pymongo import MongoClient
from datetime import date
import pandas as pd
import sys
import matplotlib.pyplot as plt

mdb = MongoClient('192.168.2.212', 27017)
reviews = mdb.amazon_brand_data.reviews_test_test

reviews_all = mdb.amazon_brand_data.reviews_test

delta = {}
# lovers = pd.DataFrame()
# haters = pd.DataFrame()
# others = pd.DataFrame()


def fetch():
	global delta
	# global lovers
	# global haters
	# global others
	result = list(reviews.find())
	all_minDates = reviews_all.aggregate([
		{
			"$group":{
				"_id": "$asin",
				"minDate" : {"$min" : "$date"}
			}
		}
	])
	dates = {}
	for i in list(all_minDates):
		dates[i['_id']] = i

	for rev in result:
		author = rev['author_id']
		product = rev['asin']
		try: query = dates[product]
		except: continue
		minDate = query['minDate']
		minDate = date(minDate[0],minDate[1],minDate[2])
		curDate = rev['date']
		curDate = date(curDate[0],curDate[1],curDate[2])
		elapsed = (curDate-minDate).days
		if(elapsed<0): continue
		try:
			delta[author].append(elapsed)
		except:
			delta[author] = [elapsed]

	df = pd.read_csv('data/params.csv', sep=';')
	new_df = []
	not_found = 0
	for i,row in df.iterrows():
		author = row['reviewer_id']
		try:
			new_df.append({'reviewer_id':author, 'avg_delay':sum(delta[author])/len(delta[author]), 'avg_rating':row['avg_rating']})
		except:
			not_found += 1
	print("Not found errors:",not_found)
	new_param = pd.DataFrame(new_df)

	# lovers = new_param[new_param['avg_rating']>=4]
	# haters = new_param[new_param['avg_rating']<=2]
	# others = new_param[(new_param['avg_rating']>2) & (new_param['avg_rating']<4)]
	# lovers.to_csv('data/lovers_time.csv', sep = ';')
	# haters.to_csv('data/haters_time.csv', sep = ';')
	# others.to_csv('data/others_time.csv', sep = ';')


# def load():
# 	global lovers
# 	global haters
# 	global others
# 	haters = pd.read_csv('data/lovers_time.csv', sep=';')
# 	lovers = pd.read_csv('data/haters_time.csv', sep=';')
# 	others = pd.read_csv('data/others_time.csv', sep=';')


# def plot():
	# fig, axes = plt.subplots(nrows=2, ncols=2)
	# ax0, ax1, ax2, ax3 = axes.flatten()
# 
	# haters['avg_delay'].hist(density=True, color='r', alpha=0.5, ax=ax0)
	# ax0.set_title('Brand Haters')
	# lovers['avg_delay'].hist(density=True, color='g', alpha=0.5, ax=ax1)
	# ax1.set_title('Brand Lovers')
	# others['avg_delay'].hist(density=True, color='b', alpha=0.5, ax=ax2)
	# ax2.set_title('Others')
	# haters['avg_delay'].hist(density=True, color='r', alpha=0.5, ax=ax3)
	# lovers['avg_delay'].hist(density=True, color='g', alpha=0.5, ax=ax3)
	# others['avg_delay'].hist(density=True, color='b', alpha=0.5, ax=ax3)
	# ax3.set_title('All')
	# plt.suptitle('Average time delay of reviewers')


def write(file):
	with open(file,'w') as f:
		for author in delta.keys():
			num = sum(delta[author])
			den = len(delta[author])
			f.write(author + ","+str(num/den)+"\n")

if __name__ == '__main__':
	fetch()
	# load()
	# plot()
	# plt.show()
	write('data/time_windows.txt')