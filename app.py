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

	import_heart_rates(retr, intraday)

def import_heart_rates(day, intraday_summary):

	# First, run through the intraday series Fitbit gives us, associating it with our day, and playing with the dates a tad.
	for sample in intraday_summary:
			sample['time'] = datetime.datetime.combine(day.date, Helper.string_to_datetime(sample['time'], 'time'))
			sample['day'] = day

	# Now check to see if we have heart rate data already for that day.
	if day.heart_rate_samples.count() == 0:
		# We have no data yet, so we import everything
		models.HeartRate.import_rates(day, intraday_summary)
	else:
		# We have some data already, so we trim down the list of data we're about to insert based on
		# what we have in the database already.
		exclusions = [hr.time for hr in day.heart_rate_samples]
		delta = list(filter(lambda x: x['time'] not in exclusions, intraday_summary))
		models.HeartRate.import_rates(day, delta)

all_days = human.get_recorded_days()

for day in all_days:
	print(day)


