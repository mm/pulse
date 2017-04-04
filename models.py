from peewee import *
from helper import Rainbow, Helper
import datetime, json

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
	resting_hr = IntegerField(default=0)

	@classmethod
	def create_day(cls, human, date):
		try:
			with DATABASE.atomic():
				return cls.create(
					human=human,
					date=date,
				)
		except IntegrityError:
			print("{}Note: A day with date {} exists in the database already.{}".format(Rainbow.yellow, date, Rainbow.endc))
			return cls.get(cls.date == date)

	def update_resting_hr(self, resting_rate):
		self.resting_hr = resting_rate
		self.save()

	@classmethod
	def get_day(cls, date=datetime.date.today()):
		return (Day.select().where(Day.date == date)).get()

	def get_heart_rate_data(self):
		return HeartRate.select().where(HeartRate.day == self)

	def prepare_hr_data_graph(self):
		# Not the most efficient thing in the world just yet.
		format_string = '%H:%M'
		graph_data = []

		# Let x be time, y be the heart rate itself

		for hr in self.heart_rate_samples:
			graph_data.append({'x': hr.time.strftime(format_string), 'y': hr.value})

		return json.dumps(graph_data)

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
