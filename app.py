from fitbit import FitbitClient
from helper import Rainbow, DatabaseHelper
import models, exceptions
import requests
import os, datetime

client_id = os.environ["FITBIT_CLIENT_ID"]

# Open up the database
models.initialize()

# See if I exist yet... Create me if I don't.
try:
	human = models.Human.select().where(models.Human.name == "Matthew Mascioni").get()
except models.DoesNotExist:
	print("He doesn't exist yet. Creating him now.")
	human = models.Human.create(name="Matthew Mascioni", access_token="")

# Set up a new instance for our Fitbit client.

fitbit_client = FitbitClient(client_id=client_id, token={'token_type': 'Bearer', 'access_token': human.access_token})

if not human.access_token:
	# We save the token our client just generated.
	human.access_token = fitbit_client.token
	human.save()

def string_to_datetime(string, type):
	if type == 'time':
		return datetime.datetime.strptime(string, '%H:%M:%S')
	elif type == 'date':
		return datetime.datetime.strptime(string, '%Y-%m-%d')

def sync_day_to_database(date=datetime.datetime.now()):
	try:
		summ, intraday = fitbit_client.fetch_heartrate_detailed_day(date=date)
	except (exceptions.InputError, ValueError):
		print("An error occured when fetching.")

	print(summ)

	#Add a new day to our database
	try:
		date_to_pass = string_to_datetime(summ['date'], 'date')
		models.Day.create_day(human, date_to_pass, summ['resting_rate'])
	except IntegrityError:
		print("Error occured when saving.")

	print(day)

	retr = (models.Day.select().where(models.Day.date == date_to_pass)).get()
	print(retr.resting_hr)

	#Prepare to bulk insert heart rates, by changing all time strings Fitbit returns to datetime objects
	for sample in intraday:
		sample['time'] = string_to_datetime(sample['time'], 'time')
		sample['day'] = retr

	#Bulk-insert heart rates for that day
	models.HeartRate.import_rates(intraday)

#sync_day_to_database(datetime.date(year=2017, month=2, day=21))

retrieved_day = (models.Day.select().where(models.Day.date == datetime.datetime(year=2017, month=2, day=21))).get()

for rate in retrieved_day.heart_rate_samples:
	print("{} \t {}".format(rate.time, rate.value))


