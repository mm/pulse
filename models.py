from peewee import *
import datetime

DATABASE = SqliteDatabase('fitbitdata.db')

class Human(Model):
	name = CharField(max_length=255, unique=True)
	access_token = CharField(max_length=512, unique=True)

	class Meta:
		database=DATABASE

class Day(Model):
	human = ForeignKeyField(Human, related_name='day_summary')
	date = DateField(default=datetime.date.today)
	resting_hr = IntegerField()

	class Meta:
		database=DATABASE

class HeartRate(Model):
	day = ForeignKeyField(Day, related_name='heart_rate_samples')
	time = TimeField()
	value = IntegerField()

	class Meta:
		database=DATABASE

def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Human, Day, HeartRate], safe=True)
	DATABASE.close()
