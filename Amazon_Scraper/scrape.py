import sys
from time import sleep
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time
import pprint
from pymongo.errors import BulkWriteError

#    ------- Initialise database --------
mdb = MongoClient('192.168.2.212', 27017)
products_db = mdb.amazon_brand_data.products_test
reviews_db = mdb.amazon_brand_data.reviews_test
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

options = Options()
options.add_argument("--headless")

browser = webdriver.Firefox(firefox_options=options)
browser_reviews = webdriver.Firefox(firefox_options=options)

# browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
# browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
# browser = webdriver.Chrome(chrome_options=options)
# browser_reviews = webdriver.Chrome(chrome_options=options)


def exit_all():
	print("Exited all windows")
	browser.close()
	browser_reviews.close()
	sys.exit(0)

exit = exit_all

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

def scrape_reviews(asin,brand,category):
	
	def getReviewPage(asin, pageNumber):
		return 'https://www.amazon.in/product-reviews/'+str(asin)+'/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&pageNumber='+str(pageNumber)
	
	try:
		pageNumber = 1
		browser_reviews.get( getReviewPage(asin,pageNumber) )
		try:
			total_reviews = int(browser_reviews.find_element_by_xpath( "//span[@data-hook='total-review-count']" ).text.replace(',',''))
		except:
			return

		print("ASIN:",asin, ", Total Reviews:", total_reviews)

		while 1:

			raw_reviews = browser_reviews.find_elements_by_xpath( '//div[@class="a-section review"][@data-hook="review"]' )

			if len(raw_reviews) == 0:
				break

			processed_review_list = []
			for raw_review in raw_reviews:
				processed_review = get_processed_review(raw_review)
				processed_review['asin'] = asin
				processed_review['brand'] = brand
				processed_review['category'] = category
				processed_review_list.append(processed_review)
			
			start = time.time()
			try:
				reviews_db.insert_many(processed_review_list,ordered=False)
			except BulkWriteError:
				pass
			except Exception as e:
				pass
			end = time.time()
			#print("Inserted in", end-start)
			#pprint.pprint(processed_review)

			print(end=".")
			sys.stdout.flush()
			pageNumber += 1
			browser_reviews.get( getReviewPage(asin,pageNumber) )

		print()

	except Exception as e:
		print(e)
		print(str(e))

def get_processed_product(raw_product):
	result = {
		'exists':True,
	}

	try:
		url = raw_product.find_element_by_xpath('.//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]').get_attribute('href')
		result['url'] = url
		result['asin'] = url[url.find('dp/')+3:url.find('dp/')+13]
		result['name'] = raw_product.find_element_by_xpath('.//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]/h2').text
		brand_line  = raw_product.find_element_by_xpath('.//span[text()="by "]')
		result['brand'] = (brand_line.find_elements_by_xpath('.//../span')[1]).text
	except:
		return False
	
	try:
		result['price'] = int(raw_product.find_element_by_xpath('.//span[@class="a-size-base a-color-price s-price a-text-bold"]').text.replace(',', ''))
	except:
		result['price'] = -1

	result['prime'] = True if raw_product.find_elements_by_xpath('.//i[@aria-label="prime"]') else False
	
	
	#result['breakup'] = {1:0, 2:0, 3:0, 4:0, 5:0}
	
	try:
		rating = raw_product.find_element_by_xpath(".//a[@href='javascript:void(0)'][@class='a-popover-trigger a-declarative']/i/span[@class='a-icon-alt']").get_attribute('innerHTML')
		result['avg_rating'] = float(rating[:rating.find(' ')])
		
		count = raw_product.find_element_by_xpath(".//a[@href='javascript:void(0)'][@class='a-popover-trigger a-declarative']/../../../a[@class='a-size-small a-link-normal a-text-normal']").get_attribute('innerHTML')
		result['review_count'] = int(count.replace(',',''))

		### TODO: Fix this rating histograms.

		# rating_box = raw_product.find_element_by_xpath(".//a[@href='javascript:void(0)'][@class='a-popover-trigger a-declarative']/i/span[@class='a-icon-alt']")

		# rating_box.location_once_scrolled_into_view
		
		# hover = ActionChains(browser).move_to_element(rating_box)
		# hover.perform()
		# WebDriverWait(browser,2).until(EC.element_to_be_clickable((By.XPATH,'.//tr[@class="a-histogram-row"]')))

		# i = 5
		# for rating_bar in raw_product.find_elements_by_xpath('//tr[@class="a-histogram-row"]'):
		# 	result['breakup'][i] = int(rating_bar.find_element_by_xpath('.//div[@class="a-meter"]').get_attribute('aria-label').replace('%',''))
		# 	i -= 1
	

	except:
		result['avg_rating'] = 0
		result['review_count'] = 0

	return result

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("No command line arguments given")
		exit()
	file_name = sys.argv[1]
	for line in open(file_name,'r'):
		s = line.split()
		base_url,category = s[0],s[1]
		try:
			browser.get(base_url)
			
			while 1:
				#browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				WebDriverWait(browser,2).until(EC.element_to_be_clickable((By.XPATH,'//a[@id="pagnNextLink"]/span[@id="pagnNextString"]')))
				products_processed = 0
				raw_products = browser.find_elements_by_xpath('//div[@class="a-row s-result-list-parent-container"]/ul/li')

				for raw_product in raw_products:
					processed_product = get_processed_product(raw_product)
					if processed_product == False:
						continue
					processed_product['category'] = category
					
					try:
						products_db.insert_many([processed_product],ordered=False)
						pprint.pprint(processed_product['url'])
						scrape_reviews(processed_product['asin'],processed_product['brand'],category)
					except BulkWriteError as e:
						print(str(e))
					except Exception as e:
						print(str(e))
					
				
				try:
					browser.find_element_by_xpath('//span[@id="pagnNextString"]').click()
					sleep(0.1)
				except Exception as e:
					print(str(e))

		except Exception as e:
			print(e)
			print(str(e))
		print("Category", category, "done")

	browser.close()
	browser_reviews.close()
