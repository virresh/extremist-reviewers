import sys, traceback
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
import signal

#    ------- Initialise database --------
mdb = MongoClient('192.168.2.212', 27017)
reviews_db = mdb.amazon_brand_data.reviews_test_test
#    ------------------------------------
browser = None
options = Options()
options.add_argument("--headless")

def exit_all(signal=None, frame=None):
    global browser
    print("Exiting by closing browser")
    if browser:
        browser.quit()
    sys.exit(0)

exit = exit_all

def get_brand_from_asin(asin):
    url = f"https://www.amazon.in/dp/{asin}"
    try:
        browser.get(url)
        brand = browser.find_element_by_xpath('//*[@id="bylineInfo"]').text
        if brand:
            return brand
    except Exception as e:
        print('No brand for {}'.format(asin))
        # traceback.print_exc()
    return None

def fix_missing():
    empty_branded_prods = reviews_db.aggregate(
            [
                {
                    "$match":{
                        "brand":""
                    }
                },
                {
                    "$group" : {
                       "_id": {
                            "product_asin":"$asin"
                       },
                       "entry":{
                            "$push":{
                                "_id":"$_id",
                            }
                        },
                       "count": {"$sum": 1},
                    }
                },
                {
                    "$sort":{
                        "count":-1
                    }
                }
            ], allowDiskUse=True
    )

    for i, product in enumerate(empty_branded_prods):
        asin = product['_id']['product_asin']
        brand = get_brand_from_asin(asin)
        print(asin, brand)
        if brand:
            ids = [x['_id'] for x in product['entry']]
            reviews_db.update_many({ "_id": { "$in": ids }}, { "$set": { "brand": brand }});
        # if i >= 10: break


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_all)
    try:
        browser = webdriver.Firefox(firefox_options=options)
        # browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
        fix_missing()
    except Exception as e:
        traceback.print_exc()
    finally:
        exit_all()

"""
empty_branded_prods = reviews.aggregate(
            [
                {
                    "$match":{
                        "brand":""
                    }
                },
                {
                    "$group" : {
                       "_id": {
                            "product_asin":"$asin"
                       },
                       "entry":{
                            "$push":{
                                "_id":"$_id",
                            }
                        },
                       "count": {"$sum": 1},
                    }
                },
                {
                    "$sort":{
                        "count":-1
                    }
                }
            ], allowDiskUse=True
    );

t = next(empty_branded_prods)
print(t)
"""
