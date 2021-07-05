import time, random
from flask import Flask, request
from sqlalchemy import text, create_engine
import xml.etree.ElementTree as ET

app = Flask(__name__)
engine = create_engine("sqlite+pysqlite:///db/crummy.db", echo=False, future=True)

def updateRecipeIngredients():
    '''
    Update RecipeIngredients table
    '''
    with engine.connect() as conn:
        ingredients_db = conn.execute(text('SELECT Name, Quantity, Unit, Form FROM Ingredient'))
        ingredients_db_records = [{'Name':row[0], 'Quantity':row[1], 'Unit':row[2], 'Form':row[3]} for row in list(ingredients_db)]

    with engine.connect() as conn:
        recipes = conn.execute(text('SELECT * FROM Recipe'))
        for recipe in recipes:
            ingredients_root = ET.fromstring(recipe.Ingredients)
            ingredient_tag_details = [{t.tag:t.text for t in list(child)} for child in ingredients_root.findall('./Ingredient')]
            ingredient_tag_count = len(ingredient_tag_details)
            ingredient_db_count = 0
            for row in ingredient_tag_details:
                db_results = next(record['Name'] for record in ingredients_db_records if record['Name'] == row['Name'])
                if len(db_results) > 0: ingredient_db_count += 1

            print("Tag", ingredient_tag_count, "DB", ingredient_db_count)
            if ingredient_tag_count == ingredient_db_count:
                print("Tag", ingredient_tag_count, "DB", ingredient_db_count)

@app.route('/ingredients/', methods=['GET'])
def get_ingredients():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM Ingredient'))
        return {row.ID:{'Name':row.Name, 'Quantity':row.Quantity, 'Unit':row.Unit, 'Form':row.Form} for row in result}

@app.route('/recipes/', methods=['GET'])
def get_recipes():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM Recipe'))
        return {row.ID:{'Name':row.Name, 'Description':row.Description, 'Ingredients':row.Ingredients, 'Instructions':row.Instructions} for row in result}

@app.route('/filtered_recipes/', methods=['GET'])
def filtered_recipes():
    sql = 'SELECT R.Name, R.Description FROM Recipe R INNER JOIN RecipeIngredient RI ON Recipe.ID=RI.RecipeID'
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return {row.ID:{'Name':row.Name, 'Description':row.Description, 'Ingredients':row.Ingredients, 'Instructions':row.Instructions} for row in result}

@app.route('/delete/<id>/<table>', methods=['GET'])
def delete(id, table):
    with engine.connect() as conn:
        result = conn.execute(text(f'DELETE FROM {table.capitalize()} WHERE ID = {id}'))
        conn.commit()

@app.route('/add_ingredient/', methods=['POST'])
def add_ingredient():
    # Data will be received as a POST HTTP message
    data = request.get_json()
    ingredient_name = data['ingredient_name']
    ingredient_quantity = data['ingredient_quantity']
    ingredient_unit = data['ingredient_unit']

    # Data will then be added as a record in the database
    with engine.connect() as conn:
        result = conn.execute(
            text('INSERT INTO Ingredient (i, n, q, u) VALUES (:i, :n, :q, :u)'),
            [{"i":round(random.random() * 1000), "n":ingredient_name, "q":ingredient_quantity, "u":ingredient_unit}]
        )
        conn.commit()

@app.route('/add_recipe/', methods=['POST'])
def add_recipe():
    # Data will be received as a POST HTTP message
    data = request.get_json()
    recipe_name = data['recipe_name']
    recipe_description = data['recipe_description']
    recipe_ingredients = data['recipe_ingredients']
    recipe_instructions = data['recipe_instructions']

    # Data will then be added as a record in the database
    with engine.connect() as conn:
        result = conn.execute(
            text('INSERT INTO Recipe (i, n, d, ing, ins) VALUES (:i, :n, :d, :ing, :ins)'),
            [{"i":round(random.random() * 1000), "n":recipe_name, "d":recipe_description, "ing":recipe_ingredients, "ins":recipe_instructions}]
        )
        conn.commit()

    updateRecipeIngredients()
