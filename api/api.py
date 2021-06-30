import time, random
from flask import Flask, request
from sqlalchemy import text, create_engine

app = Flask(__name__)
engine = create_engine("sqlite+pysqlite:///db/crummy.db", echo=False, future=True)

@app.route('/ingredients/', methods=['GET'])
def get_ingredients():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM Ingredient'))
        return {row.ID:{'Name':row.Name, 'Quantity':row.Quantity, 'Unit':row.Unit} for row in result}

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
