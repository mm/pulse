from peewee import *
from helper import Rainbow, Helper
import datetime, json

DATABASE = SqliteDatabase('fitbitdata.db')

class Human(Model):
	name = CharField(max_length=255, unique=True)
	access_token = CharField(max_length=512, unique=True)

	def clear_token(self):
		"""Clears the OAuth access token."""
		self.access_token = ""
		self.save()

	def update_access_token(self, token):
		"""Updates the OAuth access token and saves it."""
		self.access_token = token
		self.save()

	def get_recorded_days(self):
		"""Returns a query selecting all days where heart rate data has been synced."""
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
		"""Attempts to create a Day object with a specified date. If one exists already, it is returned instead.
		
		Arguments:
		human -- The Human object that will be associated with this Day.
		date -- A datetime.date object representing the date associated with this Day.
		"""
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
		"""Updates and saves the resting heart rate for a given day."""
		self.resting_hr = resting_rate
		self.save()

	@classmethod
	def get_day(cls, date=datetime.date.today()):
		"""Returns a given Day object. Pass in a datetime.date object. By default, it selects today's date."""
		return (Day.select().where(Day.date == date)).get()

	def get_heart_rate_data(self):
		"""Returns a query for associated heart rate data for a given Day object."""
		return HeartRate.select().where(HeartRate.day == self)

	def prepare_hr_data_graph(self):
		"""Returns JSON data with a time series of heart rate data, meant to be used for graphing."""
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
		"""Imports a list of heart rates, creating many HeartRate objects at once. The lists:

		- Should be lists of dictionaries, containing three keys: 'time', 'day' and 'value'
		- 'time' should be associated with a datetime.datetime object
		- 'day' should be the associated Day object for the heart rate
		- 'value' should be an integer representing the heart rate
		"""

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
	"""Drops all Day and HeartRate tables immediately. Useful for debugging."""
	DATABASE.drop_tables([Day, HeartRate])
	print("Day and heart rate tables dropped.")
