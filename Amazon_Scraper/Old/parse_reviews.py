from tinydb import TinyDB, Query, where
import json

import parse_products as products_db

#    ------- Initialise database --------
reviews_db = TinyDB('reviews.json')
review = Query()
#    ------------------------------------

####
# Defining a review structure as :
# Review = {
#	'id' : 'Review ID', 
#	'review_url' : 'Review URL', 
# 	'author_id': 'ID of author', 
#	'asin' : 'Amazon stock ID (ASIN)', 
#	'date' : 'Date posted', 
#	'verified_purchase': 'True means verified, False otherwise', 
#	'rating' : 'Rating'
#	'title' : 'Review title', 
#   'text': 'Review text', 
#	'helpful' : 'Number of helpful upvotes'
#	'exists': 'True means review still present, False otherwise' 
# }
#
####
def rid_exists(rid):
	result = reviews_db.search(review.id == rid)
	return True if result else False
def get_by_id(rid):
	result = reviews_db.search(review.id == rid)
	if result:
		return result[0]

def rid_to_user(rid):
	result = reviews_db.search(review.id == rid)
	if result:
		return result[0]['author_id']

def users_to_products():
	tuples = {}
	all_results = reviews_db.all()
	r_ids = {}
	for result in all_results:
		a_id = result['author_id']
		if result['id'] in r_ids.keys():
			continue
		r_ids[result['id']] = 1
		key = (a_id, products_db.asin_to_brand(result['asin']))
		if key not in tuples.keys():
			tuples[key] = 0
		tuples[key] +=1
	return tuples

def users_to_brands_all():
	tuples = {}
	all_results = reviews_db.all()

	for result in all_results:
		key = (result['author_id'], products_db.asin_to_brand(result['asin']))
		if key not in tuples.keys():
			tuples[key] = 0
		tuples[key] += 1
	return tuples

def users_to_brands(category):
	tuples = {}
	all_results = reviews_db.search(review.category == category)

	for result in all_results:
		key = (result['author_id'], products_db.asin_to_brand(result['asin']))
		if key not in tuples.keys():
			tuples[key] = 0
		tuples[key] += 1
	return tuples

def users_to_reviews():
	users = {}
	all_results = reviews_db.all()
	for result in all_results:
		a_id = result['author_id']
		if a_id not in users.keys():
			users[a_id] = []
		users[a_id].append(result['id'])
	return users

def products_to_users():
	products = {}
	all_results = reviews_db.all()

	for result in all_results:
		asin = result['asin']
		if asin not in products.keys():
			products[asin] = []
		products[asin].append(result['author_id'])
	return products
def all_rids():
	r_ids = []
	all_results = reviews_db.all()
	for result in all_results:
		r_ids.append(result['id'])
	return r_ids

def all_urls():
	urls = []
	all_results = reviews_db.all()
	for result in all_results:
		urls.append(result['review_url'])
	return urls


if __name__ == "__main__":
	print(len(all_rids()))
	pass
		