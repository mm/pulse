from peewee import *
import datetime

DATABASE = SqliteDatabase('fitbitdata.db')

class Human(Model):
	name = CharField(max_length=255, unique=True)
	access_token = CharField(max_length=512, unique=True)

	def clear_token(self):
		self.access_token = ""
		self.save()

	class Meta:
		database=DATABASE

class Day(Model):
	human = ForeignKeyField(Human, related_name='day_summary')
	date = DateField(default=datetime.date.today)
	resting_hr = IntegerField()

	@classmethod
	def create_day(cls, human, date, resting_rate):
		try:
			with DATABASE.atomic():
				cls.create(
					human=human,
					date=date,
					resting_hr=resting_rate
				)
		except IntegrityError:
			print("Day already exists.")

	def update_day(self, **changes):
		try:
			for key, value in changes:
				setattr(self, key, value)
			self.save()
		except ValueError:
			pass

	class Meta:
		database=DATABASE

class HeartRate(Model):
	day = ForeignKeyField(Day, related_name='heart_rate_samples')
	time = TimeField()
	value = IntegerField()

	@classmethod
	def import_rates(cls, bulk):
		with DATABASE.atomic():
			for data_dict in bulk:
				cls.create(**data_dict)

	class Meta:
		database=DATABASE

def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Human, Day, HeartRate], safe=True)
	DATABASE.close()
