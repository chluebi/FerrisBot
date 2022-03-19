import database as db

db.PlaceProject.delete_table()
db.PlacePixel.delete_table()

db.PlaceProject.create_table()
db.PlacePixel.create_table()
