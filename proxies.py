"""
This module give proxies 
radomly from 
url : "https://free-proxy-list.net/"

country_allow = "In, Usa, Ca, Bd"
anonymity_allow = "elite"
"""

import requests as rq 
from bs4 import BeautifulSoup as bs
import random


class proxies:

	base_url = "https://free-proxy-list.net/"
	proxies_list = []
	def __init__(self):
		res = rq.get(self.base_url)
		parsed_html = bs(res.text, "html.parser")
		self.extract(parsed_html)

	def extract(self, parsed_html):
		tbody = parsed_html.find_all('tbody')
		tr = tbody[0].find_all('tr')
		country_code = ["US", "BD", "IN", "CA"]
		for i in tr:
			td = i.find_all('td')
			if td[4].text == "elite proxy" and td[2].text in country_code:
				if td[6].text == "yes":
					obj = {
					"https":"https://"+td[0].text+":"+td[1].text
					}
					self.proxies_list.append(obj)
				else:
					obj = {
					"http":"http://"+td[0].text+":"+td[1].text
					}
					self.proxies_list.append(obj)
	def get_proxy(self):
		return random.choice(self.proxies_list)


