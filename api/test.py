# Testing Python file
from api import updateRecipeIngredients
from sqlalchemy import create_engine, text
updateRecipeIngredients()
engine = create_engine('sqlite+pysqlite:///db/crummy.db', echo=False, future=True)
with engine.connect() as conn:
	print(list(conn.execute(text('SELECT * FROM RecipeIngredient'))))