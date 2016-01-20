from flask import render_template
from flaskexample import app
from mysql_wrapper import MysqlWrapper
from flask import request
from ModelIt import ModelIt

login = {'host': '127.0.0.1',
        'user': 'root',
        'db': 'yummly_database'}
db = MysqlWrapper(login)

@app.route('/')
@app.route('/index')
def index():
	return render_template('upfront.html')

@app.route('/output')
def cesareans_output():
  	recipe_name = request.args.get('recipe_name')
	
	sql = "SELECT id FROM recipes WHERE name = %s"
	recipe_ids = db.read_query(sql, (recipe_name,))

	for recipe_id in recipe_ids:
		sql = """
		SELECT recipe_ingredients.amount, recipe_ingredients.unit, ingredients.ingredient, recipe_ingredients.ingredient_id
		FROM recipe_ingredients
		JOIN ingredients
		ON recipe_ingredients.ingredient_id = ingredients.id 
		WHERE recipe_ingredients.recipe_id = %s
		"""	
		result = db.read_query(sql, (recipe_id,))
		if len(result) > 0:
			break
	
	ingredients = []
	for row in result:
		sql = """
		SELECT DISTINCT unit
		FROM recipe_ingredients
		WHERE ingredient_id = %s
		"""
		units = db.read_query(sql, (row[-1],))
		if row[0] is not None:
			ingredients.append(dict(recipe=recipe_name, amount=row[0], unit=units, content=row[2]))
		else:
			ingredients.append(dict(recipe=recipe_name, amount="", unit=units, content=row[2]))
		recipe_name = ""

	return render_template("output.html", ingredients=ingredients) 
