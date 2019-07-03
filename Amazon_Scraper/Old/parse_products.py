from tinydb import TinyDB, Query, where
import json

#    ------- Initialise database --------
products_db = TinyDB('products.json')
product = Query()
#    ------------------------------------

####
# Defining a product structure as :
# Product = {
#	'exists': 'True means prodcut still present, False otherwise' 
#	'url' : 'Product URL', 
#	'asin' : 'ASIN', 
# 	'name': 'Name of product', 
#	'brand' : 'Product brand' ,
#	'price': 'Price of product (at time of scraping)', 
#	'prime': 'Amazon prime product or not', 
#	'avg_rating' : 'Average rating of the product', 
#	'review_count' : 'Total reviews for the product'
#	'breakup' : { ( 1 : ... ), ( 2 : ... ), ( 3 : ... ), ( 4 : ... ), ( 5 : ... )}
# }
#
####

def onAmazon(asin):
	result = products_db.search(product.asin == asin)
	if result:
		return True
	else:
		return False

def asin_to_brand(asin):
	result = products_db.search(product.asin == asin)
	if result:
		return result[0]['brand']

def asin_to_category(asin):
	result = products_db.search(product.asin == asin)
	if result:
		return result[0]['category']

def getReviewCount(asin):
	result = products_db.search(product.asin == asin)
	if result:
		return result[0]['review_count']

def allAsin(price = 0):
	asin = []
	for record in products_db.all():
		if price == 0 or (record['asin'] != None and record['price'] >= price):
			asin.append(record['asin'])
	return asin

def allAsin(category):
	asin = []
	for record in products_db.search(product.category == category):
		if record['asin'] != None:
			asin.append(record['asin'])
	return asin

def getUrl(asin):
	result = products_db.search(product.asin == asin)
	if result:
		return result[0]['amazon_url']

def allUrl():
	amazon_url = []
	for record in products_db.all():
		if record['url'] != None:
			amazon_url.append(record['url'])
	return amazon_url


if __name__ == "__main__":
	print(sum([getReviewCount(asin) for asin in allAsin()]))
	pass