import requests
from mysql_wrapper import MysqlWrapper

class Downloader(object):
	def download(self, url):
		login = {'host': '127.0.0.1',
			'user': 'root',
			'db': 'yummly_database'}
		db = MysqlWrapper(login)		
		recipe_id = url.split('/')[-1]
		if len(db.read_query("SELECT page_id FROM recipes WHERE page_id = %s", (recipe_id,))) > 0:
			return None
		else:
			url = 'http://www.yummly.com' +  url + "?unitType=imperial&servings=8"
			print url
			try:            
				r = requests.get(url)
				return r.text
			except:
				return None
