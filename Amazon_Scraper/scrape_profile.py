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
from pprint import pprint
from pymongo.errors import BulkWriteError

#    ------- Initialise database --------
mdb = MongoClient('192.168.2.212', 27017)
reviews_db_new = mdb.amazon_brand_data.reviews_test_test
reviews_db_old = mdb.amazon_brand_data.reviews_test
reviewer_db = mdb.amazon_brand_data.reviewers_test
#    ------------------------------------

options = Options()
options.add_argument("--headless")

def exit_all():
	print("Exited all windows")
	browser.close()
	browser_2.close()
	sys.exit(0)

exit = exit_all

def get_processed_review(review_link):
	pos = review_link.find("/gp/customer-reviews/")
	rid = review_link[pos+21:review_link.find('?',pos+21)]
	# if(reviews_db_old.count({"id":rid})):
	# 	return

	if(reviews_db_new.count({"id":rid})):
		return
		
	print(rid, reviews_db_new.count({"id":rid}))
	browser_2.get(review_link)
	raw_review = browser_2.find_element_by_xpath('.//div[@data-hook="review"]')
	result = { 'exists':True, }
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
	
	product_name = browser_2.find_element_by_xpath('.//a[@data-hook="product-link"]')
	asin = product_name.get_attribute('href')
	result['asin'] = asin[asin.find('dp/')+3:asin.find('dp/')+13]
	
	try:
		result['brand'] = browser_2.find_element_by_xpath('.//a[@data-hook="product-link"]/../../div/a[@class="a-size-base a-link-normal"]').text
	except:
		result['brand'] = ""	

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

browser = webdriver.Firefox(firefox_options=options)
browser_2 = webdriver.Firefox(firefox_options=options)

# browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
# browser_2 = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)

if __name__ == '__main__':
	
	# if len(sys.argv) < 2:
	# 	print("No command line arguments given")
	# 	exit()
	# file_name = sys.argv[1]
	file_name = './housekeeping/coupling.txt'
	f = open('no_reviews.txt','w')
	f.close()
	for line in open(file_name,'r'):
		s = line.split(',')
		user = s[0]
		if(reviewer_db.count({"id":user})):
			print("User", user ,"exists in DB, skipped")
			continue
		base_url = 'https://www.amazon.in/gp/profile/amzn1.account.'+user
		for i in range(7):
			try:
				browser.get(base_url)
				wait = wait = WebDriverWait(browser, 10)
				try:
					wait.until(EC.presence_of_element_located((By.XPATH, './/span[text()="reviews" and @class="a-size-small a-color-base"]/../../div[@class="dashboard-desktop-stat-value"]/span')))
				except TimeoutException:
					print('The element appears')
				author_name = browser.find_element_by_xpath('.//div[@class="a-row a-spacing-none name-container"]/span').text
				total_reviews = browser.find_element_by_xpath('.//span[text()="reviews" and @class="a-size-small a-color-base"]/../../div[@class="dashboard-desktop-stat-value"]/span').text
				total_helpful = browser.find_element_by_xpath('.//span[text()="helpful votes" and @class="a-size-small a-color-base"]/../../div[@class="dashboard-desktop-stat-value"]/span').text
				total_reviews = int(total_reviews.replace(',','').replace('.','').replace('k','00').replace('m','00000'))
				total_helpful = int(total_helpful.replace(',','').replace('.','').replace('k','00').replace('m','00000'))
				try:
					ranking = browser.find_element_by_xpath('.//span[text()="Reviewer ranking" and @class="a-size-base"]/../div[@class="a-row"]/span[@class="a-size-base"]').text
					ranking = int(ranking.replace(',','').replace('#',''))
				except:
					ranking = 0
				print(user, total_helpful,total_reviews,ranking)
				reviewer = {}
				reviewer['id'] = user
				reviewer['name'] = author_name
				reviewer['rank'] = ranking
				reviewer['total_reviews'] = total_reviews
				reviewer['total_helpful'] = total_helpful
				reviewer['reviews_found'] = False if browser.find_elements_by_xpath('.//span[text()="' + author_name + ' has no activity to share."]') else True
				
				try:
					reviewer_db.insert_many([reviewer],ordered = False)
				except BulkWriteError as e:
					print(str(e))
					break
				except Exception as e:
					print(str(e))
				
				if browser.find_elements_by_xpath('.//span[text()="' + author_name + ' has no activity to share."]'):
					f = open('no_reviews.txt','a')
					f.write(user+'\n')
					f.close()
					break
				processed_reviews = 0
				i = 0
				while i<2*total_reviews:
					links = browser.find_elements_by_xpath('.//a[text()="See full review" and @class="a-link-normal profile-at-review-link a-text-normal"]')
					if i == len(links):
						break
					element = links[i]
					i += 1
					browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
					review_link = element.get_attribute('href')
					processed = get_processed_review(review_link)
					if processed:
						#pprint(processed)
						try:
							reviews_db_new.insert_many([processed],ordered=False)
						except BulkWriteError as e:
							print(str(e))
						except Exception as e:
							print(str(e))
					#pprint(processed)
				print("Fetched",i)
				break
			except Exception as e:
				print(e)
				print(str(e))
				sleep(60)
		# exit()
		
	exit()
