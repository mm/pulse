from fitbit import FitbitClient
from helper import Rainbow, Helper
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

def sync_day_to_database(date=datetime.datetime.now()):
	# Grab a summary of the day, with heart rate data, from Fitbit
	try:
		summ, intraday = fitbit_client.fetch_heartrate_detailed_day(date=date)
	except (exceptions.InputError, ValueError):
		print("An error occured when fetching.")

	# Add a new day to our database
	date_to_pass = Helper.string_to_datetime(summ['date'], 'date')
	models.Day.create_day(human, date_to_pass, summ['resting_rate'])

	# Retrieve the day we added, and we'll associate this with heart rates later on.
	retr = (models.Day.select().where(models.Day.date == date_to_pass)).get()

	import_or_update_rates(retr, intraday)

def import_or_update_rates(day, intraday_summary):

	for sample in intraday_summary:
			sample['time'] = datetime.datetime.combine(day.date, Helper.string_to_datetime(sample['time'], 'time'))
			sample['day'] = day

	if day.heart_rate_samples.count() == 0:
		print("No heart rate samples, currently. Importing all of them.")
		models.HeartRate.import_rates(day, intraday_summary)
	else:
		print("We already have some heart rate values in place. Excluding some from our dataset.")
		exclusions = [hr.time for hr in day.heart_rate_samples]
		delta = list(filter(lambda x: x['time'] not in exclusions, intraday_summary))

		models.HeartRate.import_rates(day, delta)

# sync_day_to_database(date=datetime.datetime(year=2017, month=3, day=14))

retrieved_day = models.Day.get_day(datetime.datetime(year=2017, month=3, day=14))

for hr in retrieved_day.heart_rate_samples:
	print("{} {}".format(hr.time, hr.value))


