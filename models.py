from peewee import *

DATABASE = SqliteDatabase('fitbitdata.db')

class Human(Model):
	name = CharField(max_length=255, unique=True)
	access_token = CharField(max_length=512, unique=True)

	class Meta:
		database=DATABASE

def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Human], safe=True)
	DATABASE.close()
