from time import sleep
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import time
from tinydb import TinyDB, Query
import pprint

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

options = Options()
options.add_argument("--headless")
# browser = webdriver.Firefox(firefox_options=options)

browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)

def get_processed_product(raw_product):
	result = {
		'exists':True,
	}

	try:
		url = raw_product.find_element_by_xpath('.//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]').get_attribute('href')
		result['url'] = url
		result['asin'] = url[url.find('dp/')+3:url.find('dp/')+13]
		result['name'] = raw_product.find_element_by_xpath('.//a[@class="a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"]/h2').text
		# result['brand'] = (raw_product.find_elements_by_xpath('.//div[@class="a-row a-spacing-mini"]/div[@class="a-row a-spacing-none"]/span[@class="a-size-small a-color-secondary"]')[1]).text
		result['brand'] = (raw_product.find_elements_by_xpath('.//div[@class="a-row a-spacing-small"]/div[@class="a-row a-spacing-none"]/span[@class="a-size-small a-color-secondary"]')[1]).text
	except:
		return False
	
	try:
		result['price'] = int(raw_product.find_element_by_xpath('.//span[@class="a-size-base a-color-price s-price a-text-bold"]').text.replace(',', ''))
	except:
		result['price'] = -1

	result['prime'] = True if raw_product.find_elements_by_xpath('.//i[@aria-label="prime"]') else False
	
	
	result['breakup'] = {1:0, 2:0, 3:0, 4:0, 5:0}
	
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


base_url = "https://www.amazon.in/s/ref=lp_1389396031_il_to_electronics?rh=n%3A976419031%2Cn%3A%21976420031%2Cn%3A1389375031%2Cn%3A1389396031&ie=UTF8&qid=1533852230&lo=none"
category = "tv"
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
			if products_db.search(product.processed_product['asin'].exists()):
				pass
			else:
				products_db.insert(processed_product)
				products_processed += 1
			# pprint.pprint(processed_product)

		print("Processed", products_processed, "products on current page.")
		try:
			browser.find_element_by_xpath('//a[@id="pagnNextLink"]/span[@id="pagnNextString"]').click()
			sleep(0.5)
		except:
			break

except Exception as e:
	print(e)
	print(str(e))

browser.close()
