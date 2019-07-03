import pandas as pd
import matplotlib.pyplot as plt

from random import randint
def sample(df, sample_size=250, iter=40):
	d = df.to_dict(orient='records')
	l = []
	for __ in range(iter):
		indices = {}
		for i in range(sample_size):
			idx = randint(0,len(d)-1)
			l.append(d[idx])
	return pd.DataFrame(l)

scatter = pd.read_csv('data/scatter_points.csv', header=None)
scatter[0] *= 10
# mdb = MongoClient('192.168.2.212', 27017)
# reviewers_all = mdb.amazon_brand_data.reviewers_test
# result = reviewers_all.find({}, {"id":1, "rank":1, "_id":0})
# ranks = {}
# for i in list(result):
	# ranks[i['id']] = int(i['rank'])
lovers_sc = scatter[scatter[2]=='L']
haters_sc = scatter[scatter[2]=='H']
others_sc = scatter[scatter[2]=='O']

df = pd.read_csv('data/params_final.csv', sep=';')
lovers = df[(df['avg_rating']>=4)]
haters = df[(df['avg_rating']<=2)]
others = df[(df['avg_rating']>2) & (df['avg_rating']<4)]

lovers = sample(lovers)
haters = sample(haters)
others = sample(others)

# Print the length of data that we have:
print('Lovers =', len(lovers), 'Haters =', len(haters), 'Others =', len(haters))

# Plot Avg Sentiment
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()


df = pd.read_csv('data/params.csv', sep=';')
haters['avg_sentiment'].hist(density=True, color='r', alpha=0.5, ax=ax0, bins=10)
ax0.set_title('Brand Haters')
lovers['avg_sentiment'].hist(density=True, color='g', alpha=0.5, ax=ax1, bins=10)
ax1.set_title('Brand Lovers')
others['avg_sentiment'].hist(density=True, color='b', alpha=0.5, ax=ax2, bins=10)
ax2.set_title('Others')
haters['avg_sentiment'].hist(density=True, color='r', alpha=0.5, ax=ax3, bins=10)
lovers['avg_sentiment'].hist(density=True, color='g', alpha=0.5, ax=ax3, bins=10)
others['avg_sentiment'].hist(density=True, color='b', alpha=0.5, ax=ax3, bins=10)
df[(df['avg_rating']<=2) & (df['avg_sentiment']>1)]['avg_sentiment'].hist(density=True, color='y', alpha=0.5, ax=ax3, bins=10)
ax3.set_title('All')
plt.suptitle('Average Sentiment of reviewers')


# Graph for special category people (Retarded people with high sentiment and low ratings)
# fig, ax0 = plt.subplots(nrows=1, ncols=1)
# df[(df['avg_rating']<=2) & (df['avg_sentiment']>1)]['avg_sentiment'].hist(density=True, color='y', alpha=0.5, ax=ax0, bins=10)
# ax0.set_title('Special Category')

# Plot average review length
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters['avg_rev_len'].hist(density=True, color='r', alpha=0.5, ax=ax0, bins=1000)
ax0.set_title('Brand Haters')
lovers['avg_rev_len'].hist(density=True, color='g', alpha=0.5, ax=ax1, bins=1000)
ax1.set_title('Brand Lovers')
others['avg_rev_len'].hist(density=True, color='b', alpha=0.5, ax=ax2, bins=1000)
ax2.set_title('Others')
haters['avg_rev_len'].hist(density=True, color='r', alpha=0.5, ax=ax3, bins=1000)
lovers['avg_rev_len'].hist(density=True, color='g', alpha=0.5, ax=ax3, bins=1000)
others['avg_rev_len'].hist(density=True, color='b', alpha=0.5, ax=ax3, bins=1000)
ax3.set_title('All')
plt.suptitle('Average Review length of reviewers')

# Plot average upvotes
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters[haters['avg_upvotes']<30]['avg_upvotes'].hist(density=True, color='r', alpha=0.5, ax=ax0, bins=100)
ax0.set_title('Brand Haters')
lovers[lovers['avg_upvotes']<30]['avg_upvotes'].hist(density=True, color='g', alpha=0.5, ax=ax1, bins=100)
ax1.set_title('Brand Lovers')
others[others['avg_upvotes']<30]['avg_upvotes'].hist(density=True, color='b', alpha=0.5, ax=ax2, bins=100)
ax2.set_title('Others')
haters[haters['avg_upvotes']<30]['avg_upvotes'].hist(density=True, color='r', alpha=0.5, ax=ax3, bins=100)
lovers[lovers['avg_upvotes']<30]['avg_upvotes'].hist(density=True, color='g', alpha=0.5, ax=ax3, bins=100)
others[others['avg_upvotes']<30]['avg_upvotes'].hist(density=True, color='b', alpha=0.5, ax=ax3, bins=100)
ax3.set_title('All')
plt.suptitle('Average upvotes of reviewers')


# Plot sentiment vs review length
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters_sc.plot.scatter(0,1, color='r', alpha=0.5, ax=ax0)
ax0.set_title('Brand Haters')
lovers_sc.plot.scatter(0,1, color='g', alpha=0.5, ax=ax1)
ax1.set_title('Brand Lovers')
others_sc.plot.scatter(0,1, color='b', alpha=0.5, ax=ax2)
ax2.set_title('Others')
haters_sc.plot.scatter(0,1, color='r', alpha=0.5, ax=ax3)
lovers_sc.plot.scatter(0,1, color='g', alpha=0.5, ax=ax3)
others_sc.plot.scatter(0,1, color='b', alpha=0.5, ax=ax3)
ax3.set_title('All')
plt.suptitle('Average Sentiment vs Review length')

# Average Time Delay Plots
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters['avg_delay'].hist(density=True, color='r', alpha=0.5, ax=ax0)
ax0.set_title('Brand Haters')
lovers['avg_delay'].hist(density=True, color='g', alpha=0.5, ax=ax1)
ax1.set_title('Brand Lovers')
others['avg_delay'].hist(density=True, color='b', alpha=0.5, ax=ax2)
ax2.set_title('Others')
haters['avg_delay'].hist(density=True, color='r', alpha=0.5, ax=ax3)
lovers['avg_delay'].hist(density=True, color='g', alpha=0.5, ax=ax3)
others['avg_delay'].hist(density=True, color='b', alpha=0.5, ax=ax3)
ax3.set_title('All')
plt.suptitle('Average time delay of reviewers')


# Plot average rating change of reviewers
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters['avg_change'].hist(density=True, color='r', alpha=0.5, ax=ax0)
ax0.set_title('Brand Haters')
lovers['avg_change'].hist(density=True, color='g', alpha=0.5, ax=ax1)
ax1.set_title('Brand Lovers')
others['avg_change'].hist(density=True, color='b', alpha=0.5, ax=ax2)
ax2.set_title('Others')
haters['avg_change'].hist(density=True, color='r', alpha=0.5, ax=ax3)
lovers['avg_change'].hist(density=True, color='g', alpha=0.5, ax=ax3)
others['avg_change'].hist(density=True, color='b', alpha=0.5, ax=ax3)
ax3.set_title('All')
plt.suptitle('Average rating change of reviewers')

# Plot average title length
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters['avg_title_len'].hist(density=True, color='r', alpha=0.5, ax=ax0)
ax0.set_title('Brand Haters')
lovers['avg_title_len'].hist(density=True, color='g', alpha=0.5, ax=ax1)
ax1.set_title('Brand Lovers')
others['avg_title_len'].hist(density=True, color='b', alpha=0.5, ax=ax2)
ax2.set_title('Others')
haters['avg_title_len'].hist(density=True, color='r', alpha=0.5, ax=ax3)
lovers['avg_title_len'].hist(density=True, color='g', alpha=0.5, ax=ax3)
others['avg_title_len'].hist(density=True, color='b', alpha=0.5, ax=ax3)
ax3.set_title('All')
plt.suptitle('Average title length')

# Plot average title length
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

haters['avg_title_sentiment'].hist(density=True, color='r', alpha=0.5, ax=ax0)
ax0.set_title('Brand Haters')
lovers['avg_title_sentiment'].hist(density=True, color='g', alpha=0.5, ax=ax1)
ax1.set_title('Brand Lovers')
others['avg_title_sentiment'].hist(density=True, color='b', alpha=0.5, ax=ax2)
ax2.set_title('Others')
haters['avg_title_sentiment'].hist(density=True, color='r', alpha=0.5, ax=ax3)
lovers['avg_title_sentiment'].hist(density=True, color='g', alpha=0.5, ax=ax3)
others['avg_title_sentiment'].hist(density=True, color='b', alpha=0.5, ax=ax3)
ax3.set_title('All')
plt.suptitle('Average title sentiment')


plt.show()
