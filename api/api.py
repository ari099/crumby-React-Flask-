import time, random
from flask import Flask, request, jsonify
from sqlalchemy import text, create_engine
import xml.etree.ElementTree as ET

app = Flask(__name__)
engine = create_engine("sqlite+pysqlite:///db/crummy.db", echo=False, future=True)

def updateRecipeIngredients():
    '''
    Update RecipeIngredients table

    Add/Remove records from RecipeIngredients table in database. If not all the Ingredients for a given recipe exist, then no relations will be recorded for that recipe
    '''
    # Remove all rows from RecipeIngredient table
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM RecipeIngredient'))
        conn.commit()

        # Get all ingredients from Ingredients table
        # Then, place in a manipulatable Python list
        db_ingredients = list(conn.execute(text('select ID, Unit, Quantity, Name from Ingredient')))
        db_ingredients = [{'ID':str(i[0]), 'Unit':str(i[1]), 'Quantity':str(i[2]), 'Name':i[3]} for i in db_ingredients]

        # Get all recipes from Recipes table
        recipes = conn.execute(text('SELECT ID, Ingredients FROM Recipe'))

        # For each recipe...
        for recipe in recipes:
            # Get the Ingredients XML...
            ingredients_root = ET.fromstring(recipe.Ingredients)
            # Convert to Python list of dictionaries for each Ingredient in Ingredients XML
            xml = [{elem.tag:elem.text for elem in ingredient if elem.tag == 'Name' or elem.tag == 'Quantity' or elem.tag == 'Unit'} for ingredient in ingredients_root]
            # Getting the amount of Ingredients in the particular recipe
            xml_size = len(xml)
            db_size = 0 # Counter variable to count how many ingredients actually appear in the database
            # Find out how many ingredients in the XML are actually present in the Ingredients table Python list
            total = []
            for elem in xml:
                results = list(filter(lambda item: item['Name'] == elem['Name'] and float(item['Quantity']) >= float(elem['Quantity']) and item['Unit'] == elem['Unit'], db_ingredients))
                # Increment counter variable
                db_size += len(results)
                total.append(results)

            # Adding new records for the matches found
            if xml_size == db_size:
                # print(total)
                for result in total:
                    with engine.connect() as conn:
                        conn.execute(text('INSERT INTO RecipeIngredient (RecipeID, IngredientID) VALUES ({0}, {1})'.format(recipe.ID, result[0]['ID'])))
                        conn.commit()

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

@app.route('/crumbs/', methods=['GET'])
def crumbs():
    updateRecipeIngredients()
    sql = 'SELECT DISTINCT R.ID, R.Name, R.Description, R.Ingredients, R.Instructions FROM Recipe R INNER JOIN RecipeIngredient RI ON R.ID=RI.RecipeID'
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return {row.ID:{'Name':row.Name, 'Description':row.Description, 'Ingredients':row.Ingredients, 'Instructions':row.Instructions} for row in result}

@app.route('/delete/<id>/<table>', methods=['DELETE'])
def delete(id, table):
    with engine.connect() as conn:
        result = conn.execute(text(f'DELETE FROM {table.capitalize()} WHERE ID = {id}'))
        conn.commit()

    updateRecipeIngredients()

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

    updateRecipeIngredients()

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

@app.route('/update_recipe/<id>', methods=['POST'])
def update_recipe(id):
    info = request.get_json()
    with engine.connect() as conn:
        conn.execute(text('UPDATE Recipe SET {1} = \'{2}\' WHERE ID = {0}'.format(id, info['field'], info['value'])))
        conn.commit()
        return jsonify(success=True)

@app.route('/update_ingredient/<id>', methods=['POST'])
def update_ingredient(id):
    info = request.get_json()
    with engine.connect() as conn:
        conn.execute(text('UPDATE Ingredient SET {1} = \'{2}\' WHERE ID = {0}'.format(id, info['field'], info['value'])))
        conn.commit()
        return jsonify(success=True)
