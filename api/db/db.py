import sqlite3
import ctypes
import xml.etree.ElementTree as ET
import random
from PyQt5 import QtWidgets

def query(sql):
   """
   Query the Database

   Execute a query on the Crummy SQLite database

   Parameters:
   sql (string): SQL query text

   Returns:
   list: Query Results
   """
   # Connect to 'finesse.db'
   db = sqlite3.connect('C:\\Users\\alore\\Documents\\Toychest\\JavaScript\\ReactJS\\crumby\\api\\db\\crummy.db')

   # Create database cursor for query execution....
   cursor = db.cursor()
   try:
      # Execute SQL Query....
      cursor.execute(sql)

      # Getting the SQL query results....
      results = cursor.fetchall()

      # Commit any new changes to the database....
      db.commit()

      # Return the results to function caller
      return results
   except sqlite3.Error as error:
      # Return any errors returned from the query....
      # app = QtWidgets.QApplication([])
      # error_dialog = QtWidgets.QErrorMessage()
      # error_dialog.showMessage("ERROR! {}".format(error.args[0]))
      # app.exec_()
      ctypes.windll.user32.MessageBoxW(0, "ERROR! {}".format(error.args[0]), "ERROR", 0)
      return []

def getAllRecipes():
    '''
    Get all recipes from database

    Query for all the recipes from the Recipe table in the database

    Returns:
    query_results(list): List of all the rows in the Recipes table
    '''
    return query("SELECT * FROM Recipe")

def updateRecipe(name, columnName, newValue):
    '''
    Update field in recipe

    Update the value of the column specified for the Recipe record in the database

    Returns:
    (void)
    '''
    query(f"UPDATE Recipe SET {columnName.capitalize()} = '{newValue}' WHERE Name == '{name}'")

def addRecipe(name, description, instructions, ingredients):
    '''
    Add new ingredient to the Ingredients table

    Add new ingredient row to the Ingredients table in the Crummy Database

    Parameters:
    name(string): Name of Recipe
    description(string): Description of Recipe
    instructions(string): Recipe instructions
    ingredients(string): Recipe ingredients
    '''
    query(f"INSERT INTO Recipe VALUES ({int(random.random()*100)}, '{name}', '{description}', '{instructions}', '{ingredients}')")

def getAllIngredients():
    '''
    Get all ingredients from database

    Query for all the ingredients from the Ingredients table in the database

    Returns:
    query_results(list): List of all the rows in the Ingredients table
    '''
    return query("SELECT * FROM Ingredient")

def addIngredient(name, quantity, unit, form):
    '''
    Add new ingredient to the Ingredients table

    Add new ingredient row to the Ingredients table in the Crummy Database

    Parameters:
    name(string): Name of Ingredient
    quantity(float): Quantity of Ingredient
    unit(string): Unit of how much of the ingredient would be
    form(string): The form the ingredient is in (chopped, etc.)
    '''
    query(f"INSERT INTO Ingredient VALUES ({int(random.random()*100)}, '{name}', {quantity}, '{unit}', '{form}')")
