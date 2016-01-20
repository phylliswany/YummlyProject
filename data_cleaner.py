from mysql_wrapper import MysqlWrapper
import enchant 
import re
import inflect

def WhetherValidData(data):
	if len(data) == 0:
		return False

	d = enchant.Dict("en_US")
	if any([(word and d.check(word)) for word in re.split("[&\s\-()\[\]\"\',\.:;]+", data[0][1])]) is False:
		# print data[0][1]
		return False

	for row in data:
		if row[4] is None:
			# print row
			return False

	return True


def InsertData(db, data):
	print data

	sql = """
	SELECT * FROM output
	WHERE recipe_id_old = %s
	"""
	recipe_id_old = db.read_query(sql, (data[0][0],))
	if len(recipe_id_old) > 0:
		return
	
	sql = """
	INSERT INTO output (recipe_id_old, recipe, salty, savory, sour, bitter, sweet, spicy)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
	"""
	db.write_query(sql, data[0][0:2]+data[0][6:])
	sql = """
	SELECT MAX(recipe_id) FROM output
	"""
	recipe_id = db.read_query(sql, "")

	p = inflect.engine()
	for row in data:
		ingredient = re.sub("[&\s\-()\[\]\"\',\.:;]+", "_", row[3]).lower()
		if p.singular_noun(ingredient) is not False:
			ingredient = p.singular_noun(ingredient)
		# print [row[3], ingredient]
		unit = row[5]
		if row[5] is not None:
			unit = row[5].lower()
			if p.singular_noun(unit) is not False:
				unit = p.singular_noun(unit)
		# print [row[5], unit] 
		
		if unit is not None:
			sql = """
			SELECT feature_id FROM feature
			WHERE ingredient = %s
			AND unit = %s
			"""
			feature_id = db.read_query(sql, (ingredient, unit))
		else:
			sql = """
			SELECT feature_id FROM feature
			WHERE ingredient = %s
			AND unit IS NULL
			"""
			feature_id = db.read_query(sql, (ingredient,))
		if len(feature_id) == 0:
			sql = """
			INSERT INTO feature (ingredient_id_old, ingredient, unit)
			VALUES (%s, %s, %s)
			"""
			db.write_query(sql, (row[2], ingredient, unit))
			if unit is not None:
				sql = """
				SELECT feature_id FROM feature
				WHERE ingredient = %s
				AND unit = %s
				"""
				feature_id = db.read_query(sql, (ingredient, unit))
			else:
				sql = """
				SELECT feature_id FROM feature
				WHERE ingredient = %s
				AND unit IS NULL
				"""
				feature_id = db.read_query(sql, (ingredient,))
		
		sql = """
		INSERT INTO input (recipe_id, feature_id, amount)
		VALUES (%s, %s, %s)
		"""
		db.write_query(sql, (recipe_id, feature_id, row[4]))	


login = {'host': '127.0.0.1',
        'user': 'root',
        'db': 'yummly_database'}
db = MysqlWrapper(login)

sql = """
SELECT MAX(recipe_id_old)
FROM output
"""
result = db.read_query(sql, "")

sql = """
SELECT
    recipes1.recipe_id1,
    recipes1.recipe_name1,
    ingredients.id,
    ingredients.ingredient,
    recipes1.ingredient_amount1,
    recipes1.ingredient_unit1,
    recipes1.recipe_salty1,
    recipes1.recipe_savory1,
    recipes1.recipe_sour1,
    recipes1.recipe_bitter1,
    recipes1.recipe_sweet1,
    recipes1.recipe_spicy1
FROM
    (SELECT recipes.id as recipe_id1,
    recipes.name as recipe_name1,
    recipes.salty as recipe_salty1,
    recipes.savory as recipe_savory1,
    recipes.sour as recipe_sour1,
    recipes.bitter as recipe_bitter1,
    recipes.sweet as recipe_sweet1,
    recipes.spicy as recipe_spicy1,
    recipe_ingredients.ingredient_id as ingredient_id1,
    recipe_ingredients.amount as ingredient_amount1,
    recipe_ingredients.unit as ingredient_unit1
    FROM recipes
    JOIN recipe_ingredients
    WHERE recipes.id = recipe_ingredients.recipe_id
    ORDER BY recipes.id) as recipes1
JOIN ingredients
WHERE recipes1.ingredient_id1 = ingredients.id 
AND recipes1.recipe_salty1 IS NOT NULL
AND recipes1.recipe_id1 > %s  
ORDER BY recipes1.recipe_id1
"""
result = db.read_query(sql, result[0])

row_id = 0
data = []
for row in result:
    if row[0] != row_id:
        row_id = row[0]
	if WhetherValidData(data):
        	InsertData(db, data)
        data = []
    else:
        data.append(row)
