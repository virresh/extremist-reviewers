from pymongo import MongoClient
import pandas as pd
import sys
from library.sentiment import SentimentAnalysis

mdb = MongoClient('192.168.2.212', 27017)
reviews = mdb.amazon_brand_data.reviews_test
df = pd.read_csv('data/ranked.csv', sep=';')
analyzer = SentimentAnalysis(filename='library/SentiWordNet.txt')

temp = sys.stdout
fp = open('data/params.csv', 'w')
points_data = open('data/scatter_points.csv', 'w')
points_title_data = open('data/scatter_title_points.csv', 'w')
sys.stdout = fp

print('reviewer_id;brand;coupling;verified;not_verified;avg_rating;avg_sentiment;avg_title_sentiment;avg_rev_len;avg_title_len;avg_upvotes')
for index, row in df.iterrows():
    res = reviews.aggregate(
            [
                {
                    "$match":{
                        "author_id": row['reviewer_id'].strip(),
                        "brand": row['brand'].strip()
                    }
                },
                {
                    "$group" : { 
                       "_id": {
                            "brand":"$brand", 
                            "aid":"$author_id"
                       },
                       "entry":{
                            "$push":{
                                "title":"$title",
                                "review_text":"$text",
                                "asin":"$asin",
                                "helpful":"$helpful"
                            }
                        },
                       "count": {"$sum": 1},
                       "avg_rating":{
                            "$avg": "$rating"
                        }
                    } 
                },
                {
                    "$sort":{
                        "count":-1
                    }
                }
            ], allowDiskUse=True
    )
    res = list(res)
    if len(res)==0:
        print(row['reviewer_id'], row['brand'], sep=',', file=sys.stderr)
    else:
        ans = res[0]
        denom = len(ans['entry'])
        num = 0                     # numerator
        title_num = 0
        r_len = 0
        title_len = 0
        upvotes = 0
        label = None
        if ans['avg_rating'] >=4:
            label = 'L'
        elif ans['avg_rating'] <=2:
            label = 'H'
        else:
            label = 'O'
        for i in ans['entry']:
            tx = analyzer.score(i['review_text'])
            title_tx = analyzer.score(i['title'])
            num = num + int(tx * 10)                   # for review text
            title_num = title_num + int(title_tx * 10) # for title 
            r_len += len(i['review_text'])
            title_len += len(i['title'])
            upvotes += i['helpful']
            print(tx, len(i['review_text']), label, row['reviewer_id'], sep=',', file=points_data)
            print(title_tx, len(i['title']), label, row['reviewer_id'], sep=',', file=points_title_data)
        avg_sentiment = num/denom
        avg_rev_len = r_len/denom
        avg_title_len = title_len/denom
        avg_upvotes = upvotes/denom
        avg_title_sentiment = title_num/denom
        # print(row['reviewer_id'], row['brand'].strip(), row['coupling'], row['total_helpful'], row['total_reviews'], row['rank'], row['ratio'] ,ans['avg_rating'], avg_sentiment, avg_rev_len, avg_upvotes, sep=',')
        print(row['reviewer_id'], row['brand'].strip(), row['coupling'], row['verified'], row['not_verified'], ans['avg_rating'], avg_sentiment, avg_title_sentiment, avg_rev_len, avg_title_len, avg_upvotes, sep=';')

sys.stdout = temp
fp.close()
points_data.close()
points_title_data.close()
# Awesome query to get average reviews directly

# db.getCollection('reviews_test_test').aggregate(
#         [
#             {
#                 "$match":{
#                     "author_id": {
#                         "$in":['AE5PR2OGJTUZSBJYOB6QIU5ZV2UQ']
#                     },
#                     "brand": "RSITM"
#                 }
#             },
#             {
#                 "$group" : { 
#                    "_id": {
#                         "brand":"$brand", 
#                         "aid":"$author_id"
#                    },
#                    "count": {"$sum": 1},
#                     "avg_rating":{
#                         "$avg": "$rating"
#                     }
#                 } 
#             },
#             {
#               "$sort":{
#                   "count":-1
#               }
#             }
#         ], {allowDiskUse:true}
# )

# x = pd.read_csv('data/../tf_idfs.csv')
