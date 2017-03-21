from peewee import *
import datetime

DATABASE = SqliteDatabase('fitbitdata.db')

class Human(Model):
	name = CharField(max_length=255, unique=True)
	access_token = CharField(max_length=512, unique=True)

	def clear_token(self):
		self.access_token = ""
		self.save()

	def update_access_token(self, token):
		self.access_token = token
		self.save()

	def get_recorded_days(self):
		return Day.select().where(Day.human == self)

	def __str__(self):
		return "Human: {}".format(self.name)

	class Meta:
		database=DATABASE

class Day(Model):
	human = ForeignKeyField(Human, related_name='day_summary')
	date = DateField(default=datetime.date.today, unique=True)
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

	@classmethod
	def get_day(cls, date=datetime.datetime.today()):
		return (Day.select().where(Day.date == date)).get()

	def get_heart_rate_data(self):
		return HeartRate.select().where(HeartRate.day == self)

	def __str__(self):
		return "{}\n Resting Heart Rate: {}\n Heart Rate Samples: {}".format(
			datetime.datetime.strftime(self.date, '%B %d, %Y'),
			self.resting_hr,
			self.get_heart_rate_data().count())

	class Meta:
		database = DATABASE
		order_by = ('-date',)

class HeartRate(Model):
	day = ForeignKeyField(Day, related_name='heart_rate_samples', on_delete='CASCADE')
	time = DateTimeField(unique=True)
	value = IntegerField()

	@classmethod
	def import_rates(cls, day_to_assign, bulk):
		with DATABASE.atomic():
			for data_dict in bulk:
				cls.create(**data_dict)

	class Meta:
		database=DATABASE

def initialize():
	DATABASE.connect()
	DATABASE.create_tables([Human, Day, HeartRate], safe=True)
	DATABASE.close()

def reset_days():
	DATABASE.drop_tables([Day, HeartRate])
	print("Day and heart rate tables dropped.")
