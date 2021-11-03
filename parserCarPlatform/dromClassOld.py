import requests
from bs4 import BeautifulSoup
from bs4.element import AttributeValueWithCharsetSubstitution
from requests.packages import urllib3
import os
from loguru import logger
class Parser:
	"""
	Класс для сбора информации с сайта Drom.ru

	Параметры: ---

	"""
	def __init__(self):
		self.HEADER = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0', 'accept' : '*/*'}

	def get_html_text(self, url, params=None):
		"""
		Метод для отправки запроса на получение страницы
		Возвращает объект класса BeautifulSoup
		"""
		proxies = {
		# "https" : "178.32.116.64:3128",
		"http" : '51.79.249.253:8080',
		"socks4" : "101.51.121.35:4153",
		"socks5" : "98.162.96.52:4145"
		# "http" : '198.199.120.102:8080'
		}
		urllib3.disable_warnings()
		r = requests.get(url, headers=self.HEADER, params=params, proxies=proxies, verify=False)
		if r.status_code == 200:
			soup = BeautifulSoup(r.text, 'html.parser')
			return soup
		elif r.status_code == 404:
			return "PAGE NOT FOUND"
		else:
			return "Undefined code"


	def get_info_fields(self, url, city):
		"""Метод для получения информации об обявлениях со страницы

		Параметры:
		url - Ссылка на страницу
		city - Город

		Возвращает словарь {model_car, url, price, average_price, city}"""
		html = self.get_html_text(url)
		if html == "PAGE NOT FOUND":
			print("Удаляю")
			return "delete"
		else:
			# Получение табличек объявлений
			fields = html.find_all('a', class_='ewrty961')
			iteration = 1
			return_dict = {}
			for item in fields:
				model_car = item.find("span", {"data-ftid":"bull_title"}).get_text(strip=True)
				list_name = model_car.split(',')
				model_car = list_name[0]
				href = item.get("href")
				price = item.find("span", {"data-ftid":"bull_price"}).get_text(strip=True)
				list_price = price.split(' ')
				price = ''
				for i in list_price:
					price += i
				price = price.replace(u'\xa0', '')
				#print(int(price))
				if 0 < int(price) <= 100000:
					average_price = '0-100'
				elif 100000 < int(price) <= 200000:
					average_price = '100-200'
				elif 200000 < int(price) <= 500000:
					average_price = '200-500'
				elif 500000 < int(price) <= 900000:
					average_price = '500-900'
				elif 900000 < int(price) <= 1500000:
					average_price = '900-1500'
				elif 1500000 < int(price) <= 2000000:
					average_price = '1500-2000'
				else:
					average_price = '2000-...'

				return_dict[iteration] = {
				"model_car" : model_car,
				"url" : href,
				"price" : price,
				"average_price" : average_price,
				"city" : city
				}
				iteration += 1
			return return_dict

	def get_info_page_field(self, url):
		"""
		Медот для извлечения информации со страницы объявления

		Параметры:
		url - Ссылка на страницу

		Возвращает словарь с данными {date_publication, number_view, url}
		"""
		#logger.add("Errors_parser.log", format="|{time}---{level}---{message}|", level="DEBUG", rotation="10 MB")
		flag = True
		while flag:
			flag = False
			html = self.get_html_text(url)

			if html == "PAGE NOT FOUND":
				return "delete"
			elif html == 'Undefined code':
				pass
			else:
				try:
				    check_delete_page = html.find("h1", class_="e18vbajn0").get_text(strip=True)
				    if check_delete_page in ['Объявление удалено!', 'Объявление не опубликовано.']:
    				
				        return "delete"
				except AttributeError:
				    pass
				try:
					number_view = int(html.find("div", class_="css-14wh0pm e1lm3vns0").get_text(strip=True))
					print(number_view)
					date_text = html.find("div", class_="css-pxeubi evnwjo70").get_text(strip=True)
				except AttributeError as error_atr:
					#logger.error(error_atr)
					flag = True
					continue
				
				# Извлечение даты из декста
				list_date = date_text.split(' ')
				date_pub = list_date[-1].split('.')
				date_publication = date_pub[2] + '-' + date_pub[1] + '-' + date_pub[0]
				# Словарь с извлечёнными данными
				dict_info = {
				"date_publication" : date_publication,
				"number_view" : number_view,
				"url" : url
				}
				return dict_info