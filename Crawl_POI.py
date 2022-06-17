from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
import time, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import concurrent.futures
from datetime import date
import os, glob
import pandas as pd
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from geopy.distance import geodesic as GD

browser = webdriver.Chrome("C:/chromedriver.exe")
browser.delete_all_cookies()
wait = WebDriverWait(browser, 100)
browser.implicitly_wait(3)

browser2 = webdriver.Chrome("C:/chromedriver.exe")
browser2.delete_all_cookies()
wait = WebDriverWait(browser2, 100)
browser2.implicitly_wait(3)

# edit dsini lokasi dan keyword
# ['Market','supermarket','convenience store','Shopping Mall','Department Store']
#  Than Hoa	19.7774822772753	105.793026931493
lat = '19.7774822772753' 
lon = '105.793026931493'
target_loc = (lat, lon)
keyword = 'Department Store'
search_target = 'Than Hoa'

master_list = []

def save_data(store_name, url_store, url_image, reviews, star, pluscode, address, lat, lon, keyword, search_target, store_class, store_lat, store_lon):
	data_dict = {}
	data_dict['shop_name'] = store_name
	data_dict['shop_url'] = url_store
	data_dict['img_url'] = url_image
	data_dict['reviews'] = reviews
	data_dict['star'] = star
	data_dict['pluscode'] = pluscode
	data_dict['address'] = address
	data_dict['lat_target'] = lat
	data_dict['lon_target'] = lon
	data_dict['keyword'] = keyword
	data_dict['Search_Target'] = search_target
	data_dict['class'] = store_class
	data_dict['store_lat'] = store_lat
	data_dict['store_lon'] = store_lon

	master_list.append(data_dict)
	print(data_dict)
	print(len(master_list))
	print('==============================================================================')
	df = pd.DataFrame(master_list)
	df.to_excel(f'{search_target}-{keyword}.xlsx', index = False)

def get_data():
	url = 'https://www.google.com/maps/?hl=en'
	browser.get(url)
	time.sleep(2)
	browser.maximize_window()
	time.sleep(2)

    #masukin coordinate
	searchbar = browser.find_element(By.XPATH, '//input[@autofocus="autofocus"]')
	searchbar.send_keys(str(lat))
	print(lat)
	time.sleep(2)
	searchbar.send_keys(' ')
	time.sleep(2)
	searchbar.send_keys(str(lon))
	print(lon)
	searchbar.send_keys(Keys.RETURN)
	time.sleep(3)
	
	#click tombol nearby
	nearby = browser.find_element(By.XPATH, '//button[@data-value="Nearby"]')
	nearby.click()
	time.sleep(2)

	#     #zoom 5 kali
	#     zoomout = driver.find_element_by_xpath('//button[@aria-label="Zoom out"]')
	#     zoomout.click()
	#     time.sleep(2)
	#     zoomout.click()
	#     time.sleep(2)
	#     zoomout.click()
	#     time.sleep(2)

	#ganti jadi search dari daftar list
	searchbar1 = browser.find_element(By.XPATH, '//input[@id="searchboxinput"]')

	time.sleep(2)
	print(keyword)
	searchbar1.send_keys(keyword)
	searchbarenter = browser.find_element(By.XPATH, '//button[@aria-label="Search"]')
	searchbarenter.click()
	time.sleep(5)

	while True:
		scrollable_div = browser.find_element(By.XPATH, '//div[@role="main"]/div[2]/div[1]')

		browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
		time.sleep(2)
		browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
		time.sleep(2)
		browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
		time.sleep(2)
		browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
		time.sleep(2)
		soup = BeautifulSoup(browser.page_source, 'html.parser')
		cards = soup.select('div[jsaction^="mouseover:pane.wfvdle"]')
		for card in cards:			
			store_name = ' '.join(card.find('div', 'NrDZNb').text.split())
			
			url_store = card.find('a')['href']
			'''uncomment klo mau ambil lokasi tokonya'''
			try:
				location = url_store.split('8m2!3d')[1].split('!15s')[0].split('!4d')
				store_lat, store_lon = location[0], location[1].split('!')[0]  
			except:
				store_lat, store_lon = '', ''
			store_loc =(store_lat, store_lon)
			distance = GD(target_loc, store_loc).km

			print("The distance between target_loc and store_loc is: ", distance)
			if distance > 30.00:
				print(f'*********************Lokasi toko {store_name} melewati 30km*********************')
				continue
			else:
				browser2.get(url_store)
				time.sleep(3)
				soup_store = BeautifulSoup(browser2.page_source, 'html.parser')
				try:
					reviews = ' '.join(soup_store.select_one('button[jsaction="pane.rating.moreReviews"]').text.split())
				except:
					reviews = ''
				try:
					star = ' '.join(soup_store.select_one('div[jsaction="pane.rating.moreReviews"] span[aria-hidden="true"]').text.split())
				except:
					star = ''
				try:
					address = ' '.join(soup_store.select_one('button[data-item-id="address"] div[jsan="7.Io6YTe,7.fontBodyMedium"]').text.split())
				except:
					address = ''
				try:
					url_image = soup_store.select_one('button[jsaction="pane.heroHeaderImage.click"] img')['src']
				except:
					url_image = ''
				try:
					pluscode = ' '.join(soup_store.select_one('button[data-tooltip="Copy plus code"] div[jsan="7.Io6YTe,7.fontBodyMedium"]').text.split())
				except:
					pluscode = ''
				try:
					store_class = ' '.join(soup_store.select_one('button[jsaction="pane.rating.category"]').text.split())
				except:
					store_class = ''

				save_data(store_name, url_store, url_image, reviews, star, pluscode, address, lat, lon, keyword, search_target, store_class, store_lat, store_lon)
		
		if soup.select_one('button[aria-label=" Next page "][disabled="true"]'):
			print("Last page reached")
			break
		elif soup.select_one('button[aria-label=" Next page "]'):
			next_page = browser.find_element(By.CSS_SELECTOR, 'button[aria-label=" Next page "]')
			browser.execute_script("arguments[0].click();", next_page)
			print("Navigating to Next Page")
			time.sleep(3)

start_time = time.time()
get_data()
print("--- %s minutes ---" % ((time.time() - start_time)/60))
browser.close()
browser2.close()