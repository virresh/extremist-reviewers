import sys
from time import sleep
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time
from tinydb import TinyDB, Query

import parse_products as db
import parse_reviews as review_handler

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
#	'author_name': 'Name of author', 
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

def getReviewPage(asin, pageNumber):
	return 'https://www.amazon.in/product-reviews/'+str(asin)+'/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&pageNumber='+str(pageNumber)

options = Options()
options.add_argument("--headless")
# browser = webdriver.Firefox(firefox_options=options)

browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)

def get_processed_review(raw_review):
	result = {
		'exists':True,
	}
	result['id'] = raw_review.get_attribute('id')

	rating = raw_review.find_element_by_xpath(".//i[@data-hook='review-star-rating']").find_element_by_tag_name('span').get_attribute('innerHTML')
	result['rating'] = float(rating[:rating.find(' ')])
	
	title = raw_review.find_element_by_xpath(".//a[@data-hook='review-title']")
	result['review_url'] = title.get_attribute('href')
	result['title'] = title.text
	
	author = raw_review.find_element_by_xpath(".//a[@data-hook='review-author']").get_attribute('href')
	result['author_id'] = author[47:75]
	result['author_name'] = raw_review.find_element_by_xpath(".//a[@data-hook='review-author']").text
	
	date = raw_review.find_element_by_xpath(".//span[@data-hook='review-date']").text[3:]
	result['date'] = time.strptime(date, '%d %B %Y')
	
	try:
		raw_review.find_element_by_xpath(".//span[@data-hook='avp-badge']")
		result['verified_purchase'] = True
	except:
		result['verified_purchase'] = False

	result['text'] = raw_review.find_element_by_xpath(".//span[@data-hook='review-body']").text

	try:
		helpful = raw_review.find_element_by_xpath(".//span[@data-hook='helpful-vote-statement']").text
		helpful = helpful[:helpful.find(' ')]
		result['helpful'] = 1 if helpful=="One" else int(helpful)
	except:
		result['helpful'] = 0

	return result

try:
	product_number = 0
	for asin in db.allAsin('tv'):
		pageNumber = 1
		browser.get( getReviewPage(asin,pageNumber) )
		try:
			total_reviews = int(browser.find_element_by_xpath( "//span[@data-hook='total-review-count']" ).text)
		except:
			continue

		product_number += 1
		print("Product #",product_number," --  ASIN:",asin, ", Total Reviews:", db.getReviewCount(asin))

		while 1:

			raw_reviews = browser.find_elements_by_xpath( '//div[@class="a-section review"][@data-hook="review"]' )

			if len(raw_reviews) == 0:
				break

			for raw_review in raw_reviews:
				processed_review = get_processed_review(raw_review)
				processed_review['asin'] = asin
				processed_review['category'] = db.asin_to_category(asin)

				if reviews_db.search(review.id.exists()) and reviews_db.search(review.id == processed_review['id']):
					pass
				else:
					reviews_db.insert(processed_review)

				# print(processed_review['author_name'], db.asin_to_brand(asin))

			print(end=".")
			sys.stdout.flush()
			pageNumber += 1
			browser.get( getReviewPage(asin,pageNumber) )

		print()

except Exception as e:
	print(e)
	print(str(e))

browser.close()
