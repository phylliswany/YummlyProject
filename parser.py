from bs4 import BeautifulSoup
from recipe import Recipe
import re
from mysql_wrapper import MysqlWrapper

class Parser(object):
	def __init__(self):
		self.recipe = None

	def parse(self, html):
		recipe = Recipe()
		soup = BeautifulSoup(html, "html.parser")

		links = soup.find_all('a', attrs={'class': 'y-image'})
		urls = []
		for link in links:
			urls.append(link['href'])

		try:
			recipe.set('recipe_id', soup.find('div', attrs={'class': 'recipe'}).find('meta', attrs={'itemprop': 'url'})['content'].split('/')[-1])
		except:
			print 'no recipe_id'
			pass
		# print recipe.get('recipe_id')

		try:
			recipe.set('recipe_name', soup.find('h1', attrs={'itemprop': 'name'}).text)
		except:
			print 'no recipe_name'
			pass
		# print recipe.get('recipe_name')
	
		try:	
			recipe.set('image', soup.find('div', attrs={'style': re.compile('^background-image')})['style'].split('\'')[-2])
		except:
			print 'no image'
			pass
		# print recipe.get('image')		

		try:
			source_info = soup.find('span', attrs={'id': 'source-name'})	
			recipe.set('source_name', source_info.find('a').text.strip())
			recipe.set('source_UID', source_info.find('a')['href'].split('/')[-1])
		except:
			print 'no source'
			pass
		# print recipe.get('source_name')
		# print recipe.get('source_UID')		

		try:
			user_info = soup.find('span', attrs={'class': 'added-by'})
			recipe.set('nickname', user_info.find('a').text.strip())
			recipe.set('username', user_info.find('a')['href'].split('/')[-1])
		except:
			print 'no user'
			pass
		# print recipe.get('nickname')
		# print recipe.get('username')
		
		try:
			recipe.set('yums', soup.find('span', attrs={'class': 'count'})['data-count'])
		except:
			print 'no yums'
			pass	
		# print recipe.get('yums')

		try:
			total_time = soup.find('li', attrs={'class': 'time-data'}).find('span', attrs={'class':'bd'}).text
			recipe.set('total_time', int(total_time))
		except:
			recipe.set('total_time', None)
		# print recipe.get('total_time')

		try:
			amountf_re = re.compile("(\d*)\s*(\d)/(\d+)([^\d]*)")
			ingredient_list = []
			ingredients = soup.find('div', attrs={'id': 'recipe-ingredients'}).find_all('li', attrs={'itemprop': 'ingredients'})
			for ingredient in ingredients:
				if not ingredient.find('span', attrs={'class': 'amount'}).find('span', attrs={'class':'fraction'}):
					amount_unit = ingredient.find('span', attrs={'class': 'amount'}).text.strip()
					if not amount_unit:
						amount = None
						unit = None
					else:
						amount_unit = amount_unit.split(' ')
						if len(amount_unit) == 1:
							amount = amount_unit[0]
							unit = None
						else:
							amount = amount_unit[0]
							unit = amount_unit[1]
				else:
					m = amountf_re.match(ingredient.find('span', attrs={'class': 'amount'}).text)
					if m:
						if m.group(1):
							amount = int(m.group(1)) + float(m.group(2)) / float(m.group(3))
						else:
							amount = float(m.group(2)) / float(m.group(3))
						unit = m.group(4).strip()
						if not unit:
							unit = None
				content = ingredient.find('strong', attrs={'class': 'name'}).text.strip()
				ingredient_list.append((amount, unit, content))
			recipe.set('ingredients', ingredient_list)
		except:
			print 'no ingredient'
			pass
		# print recipe.get('ingredients')	

		try:
			recipe.set('rating', soup.find('span', attrs={'class': 'recipe-rating-text'}).text.split(' ')[0][1:])
		except:
			print 'no rating'
			pass
		# print recipe.get('rating')

		try:
			review_list = []
			reviews = soup.find('div', attrs={'id': 'reviews-list'}).find_all('div', attrs={'class': 'star-line'})
			text_lines = soup.find('div', attrs={'id': 'reviews-list'}).find_all('div', attrs={'class': 'text-line'})
			for i in range(0, len(reviews)):
				reviewer_nickname = reviews[i].find('a', attrs={'class': 'review-user-name'}).text
				reviewer_username = reviews[i].find('a', attrs={'class': 'review-user-name'})['href'].split('/')[2]
				review_stars = len(reviews[i].find('span', attrs={'class': 'stars'}).find_all('span', attrs={'class': re.compile('full')}))
				texts = text_lines[i].text.strip()
				review_list.append((reviewer_nickname, reviewer_username, review_stars, texts))
			recipe.set('reviews', review_list)
		except:
			print 'no review'
			pass
		# print recipe.get('reviews')

		try:
			recipe.set('calories', int(soup.find('table', attrs={'class': 'calories'}).find_all('span', attrs={'class': 'calories'})[0].text))
		except:
			recipe.set('calories', None)
		# print recipe.get('calories')

		try:
			recipe.set('calories_from_fat', int(soup.find('table', attrs={'class': 'calories'}).find_all('span', attrs={'class': 'calories'})[1].text))
		except:
			recipe.set('calories_from_fat', None)
		# print recipe.get('calories_from_fat')

		mg = re.compile("[^\.\d]*([\.\d]+)\s*mg")
		g = re.compile("[^\.\d]*([\.\d]+)\s*g") 
		try:
			nutrient_list = []
			nutrients = soup.find('table', attrs={'class': 'nutrients'}).find_all('tr')
			for nutrient in nutrients:
				content = nutrient.text.split('\n')[0].strip()
				amount = nutrient.text.split('\n')[1].strip()
				if mg.match(amount):
					amount = mg.match(amount).group(1)
				elif g.match(amount):
					amount = int(float(g.match(amount).group(1)) * 1000)
				else:
					amount = None
				percentage = nutrient.text.split('\n')[-3].strip()
				if percentage:
					percentage = percentage[0:-1]
				else:
					percentage = None
				nutrient_list.append((content, amount, percentage))
			content = soup.find('div', attrs={'class': 'protein'}).text.split('\n')[1]
			amount = soup.find('div', attrs={'class': 'protein'}).text.split('\n')[2]
			if mg.match(amount):
				amount = mg.match(amount).group(1)
			elif g.match(amount):
				amount = int(float(g.match(amount).group(1)) * 1000)
			else:
				amount = None
			percentage = None
			nutrient_list.append((content, amount, percentage))
			nutrients = soup.find_all('table', attrs={'class': 'nutrients'}, limit=2)[1].find_all('tr')
			for nutrient in nutrients:
				content = nutrient.text.split('\n')[0]
				amount = None
				percentage = nutrient.text.split('\n')[3].strip()	
				if percentage:
					percentage = percentage[0:-1]
				nutrient_list.append((content, amount, percentage))
			recipe.set('nutrients', nutrient_list)
		except:
			print 'no calorie content'
			pass
		# print recipe.get('nutrients')

		try:
			taste_list = []
			tastes = soup.find('div', attrs={'class': 'taste'}).find_all('div', attrs={'class': 'ninja-level'})
			for taste in tastes:
				taste_list.append(taste['style'].split(':')[-1][0:-1])
			recipe.set('tastes', taste_list)
		except:
			print 'no flavor'
			pass
		# print recipe.ge('tastes')

		try:
			tag_list = []
			tags = soup.find('div', attrs={'class': 'recipe-tags'}).find_all('a')
			for tag in tags:
				tag_list.append(tag.text)
			recipe.set('tags', tag_list)
		except:
			print 'no tag'
			pass
		# print recipe.get('tags')

		self.recipe = recipe		

		return urls
		
	def save(self):
		login = {'host': '127.0.0.1',
			'user': 'root',
			'db': 'yummly_database'}
		db = MysqlWrapper(login)

		try:
			source_id = db.read_query("SELECT id FROM source WHERE UID = %s", (self.recipe.get('source_UID'),))
			if len(source_id) == 0:
				db.write_query("INSERT INTO source (name, UID) VALUES (%s, %s)", (self.recipe.get('source_name'), self.recipe.get('source_UID')))
				source_id = db.read_query("SELECT id FROM source WHERE UID = %s", (self.recipe.get('source_UID'),))
		except:
			print 'cannot write source'
			source_id = None
			
		try:		
			user_id = db.read_query("SELECT id FROM users WHERE username = %s", (self.recipe.get('username'),))	
			if len(user_id) == 0:
				db.write_query("INSERT INTO users (username, nickname) VALUES (%s, %s)", (self.recipe.get('username'), self.recipe.get('nickname')))
				user_id = db.read_query("SELECT id FROM users WHERE username = %s", (self.recipe.get('username'),))
		except:
			print 'cannot write user'
			user_id = None

		
		try: 		
			recipe_id = db.read_query("SELECT id FROM recipes WHERE page_id = %s", (self.recipe.get('recipe_id'),))
			if len(recipe_id) == 0:
				db.write_query("INSERT INTO recipes (page_id, name, image, source_id, user_id, yums, total_time, rating, calories, calories_from_fat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (self.recipe.get('recipe_id'), self.recipe.get('recipe_name'), self.recipe.get('image'), source_id, user_id, self.recipe.get('yums'), self.recipe.get('total_time'), self.recipe.get('rating'), self.recipe.get('calories'), self.recipe.get('calories_from_fat')))
				recipe_id = db.read_query("SELECT id FROM recipes WHERE page_id = %s", (self.recipe.get('recipe_id'),))

				try:	
					ingredients = self.recipe.get('ingredients')
					for ingredient in ingredients:
						ingredient_id = db.read_query("SELECT id FROM ingredients WHERE ingredient = %s", (ingredient[2],))
						if len(ingredient_id) == 0:
							db.write_query("INSERT INTO ingredients (ingredient) VALUES (%s)", (ingredient[2],))
							ingredient_id = db.read_query("SELECT id FROM ingredients WHERE ingredient = %s", (ingredient[2],))
						db.write_query("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit) VALUES (%s, %s, %s, %s)", (recipe_id, ingredient_id, ingredient[0], ingredient[1]))
				except:
					print 'cannot write ingredient'
					pass

				try:
					tags = self.recipe.get('tags')
					for tag in tags:
						db.write_query("INSERT INTO recipe_tags (recipe_id, tag) VALUES (%s, %s)", (recipe_id, tag))
				except:
					print 'cannot write tag'
					pass

				try:
					reviews = self.recipe.get('reviews')
					for review in reviews:
						user_id = db.read_query("SELECT id FROM users WHERE username = %s", (review[1],))
						if len(user_id) == 0:
							db.write_query("INSERT INTO users (username, nickname) VALUES (%s, %s)", (review[1], review[0]))
							user_id = db.read_query("SELECT id FROM users WHERE username = %s", (review[1],))
						db.write_query("INSERT INTO reviews (recipe_id, user_id, rating, content) VALUES (%s, %s, %s, %s)", (recipe_id, user_id, review[2], review[3]))
				except:
					print 'cannot write review'
					pass

				
				try:
					db.write_query("UPDATE recipes SET total_fat = %s, total_fat_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[0][1], self.recipe.get('nutrients')[0][2], recipe_id))
					db.write_query("UPDATE recipes SET sat_fat = %s, sat_fat_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[1][1], self.recipe.get('nutrients')[1][2], recipe_id))
					db.write_query("UPDATE recipes SET trans_fat = %s, trans_fat_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[2][1], self.recipe.get('nutrients')[2][2], recipe_id))
					db.write_query("UPDATE recipes SET cholesterol = %s, cholesterol_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[3][1], self.recipe.get('nutrients')[3][2], recipe_id))
					db.write_query("UPDATE recipes SET sodium = %s, sodium_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[4][1], self.recipe.get('nutrients')[4][2], recipe_id))
					db.write_query("UPDATE recipes SET potassium = %s, potassium_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[5][1], self.recipe.get('nutrients')[5][2], recipe_id))
					db.write_query("UPDATE recipes SET carb = %s, carb_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[6][1], self.recipe.get('nutrients')[6][2], recipe_id))
					db.write_query("UPDATE recipes SET fiber = %s, fiber_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[7][1], self.recipe.get('nutrients')[7][2], recipe_id))
					db.write_query("UPDATE recipes SET sugar = %s, sugar_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[8][1], self.recipe.get('nutrients')[8][2], recipe_id))
					db.write_query("UPDATE recipes SET protein = %s, protein_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[9][1], self.recipe.get('nutrients')[9][2], recipe_id))
					db.write_query("UPDATE recipes SET VA_dv = %s, VC_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[10][2], self.recipe.get('nutrients')[11][2], recipe_id))
					db.write_query("UPDATE recipes SET calcium_dv = %s, iron_dv = %s WHERE id = %s", (self.recipe.get('nutrients')[12][2], self.recipe.get('nutrients')[13][2], recipe_id))
					db.write_query("UPDATE recipes SET salty = %s, savory = %s, sour = %s, bitter = %s , sweet = %s, spicy = %s  WHERE id = %s", (self.recipe.get('tastes')[0], self.recipe.get('tastes')[1], self.recipe.get('tastes')[2], self.recipe.get('tastes')[3], self.recipe.get('tastes')[4], self.recipe.get('tastes')[5], recipe_id))
				except:
					print 'cannot write calorie content'
					pass
					
		except:
			print 'cannot write recipe'
			print self.recipe.data
			pass
