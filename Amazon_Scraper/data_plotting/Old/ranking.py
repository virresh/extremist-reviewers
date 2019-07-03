from time import sleep
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import sys

options = Options()
options.add_argument("--headless")
#browser = webdriver.Firefox(firefox_options=options)

browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
ranking = []
with open("hist_files.txt","r") as f:
	for line in f:
		l = line.split()
		user = l[0][:-1]
		coupling = int(l[-1])
		for i in range(7):
			browser.get("https://www.amazon.in/gp/profile/amzn1.account."+user)
			try:
				tags = browser.find_element_by_xpath('//span[contains(text(),"reviews")]')
				total_reviews = 1
				tags = tags.find_element_by_xpath('.//../../div/span[@class="a-size-large a-color-base"]')
				total_reviews = int(tags.get_attribute('innerHTML'))
				ranking.append((user,coupling/int(total_reviews),coupling, int(total_reviews)))
				break
			except:
				sleep(60)
		print(end=".")
		sys.stdout.flush()

for i in range(len(ranking)):
	for j in range(i+1,len(ranking)):
		if ranking[i][1] < ranking[j][1]:
			ranking[i],ranking[j] = ranking[j],ranking[i]

with open('ranks.txt','w') as f:
	for tup in ranking:
		f.write(str(tup[0]) + ' ' + str(tup[1]) + ' ' + str(tup[2]) + ' ' + str(tup[3]) + '\n')
