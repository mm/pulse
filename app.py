from fitbit import FitbitClient
from helper import Rainbow, Helper
from flask import Flask, render_template, flash, url_for
import models, exceptions
import requests
import os, datetime

client_id = os.environ["FITBIT_CLIENT_ID"]
DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)

def sync_day_to_database(date=datetime.datetime.now()):
	# Grab a summary of the day, with heart rate data, from Fitbit
	try:
		summ, intraday = fitbit_client.fetch_heartrate_detailed_day(date=date)

		# Add a new day to our database
		date_to_pass = Helper.string_to_datetime(summ['date'], 'date')
		models.Day.create_day(human, date_to_pass, summ['resting_rate'])

		# Retrieve the day we added, and we'll associate this with heart rates later on.
		retr = (models.Day.select().where(models.Day.date == date_to_pass)).get()

		import_heart_rates(retr, intraday)

	except (exceptions.InputError, exceptions.ImportingError, ValueError) as e:
		print(e)

def import_heart_rates(day, intraday_summary):

	# First, run through the intraday series Fitbit gives us, preparing it for insertion in the database.
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

@app.route("/")
def index():
	retrieved_day = models.Day.get_day(datetime.datetime(year=2017, month=3, day=21))
	return "Hello! Info for yesterday: {}".format(retrieved_day.resting_hr)

if __name__ == '__main__':
	models.initialize()

	# See if I exist yet... Create me if I don't.
	human, created = models.Human.get_or_create(name = 'Matthew Mascioni', defaults={'access_token': ''})

	# Set up a new instance for our Fitbit client.
	fitbit_client = FitbitClient(client_id=client_id, token={'token_type': 'Bearer', 'access_token': human.access_token})

	if created:
		# Our user is new, so we save the token that fitbit_client just generated so we can make requests in the future.
		human.update_access_token(fitbit_client.token)

	app.run(debug=DEBUG, host=HOST, port=PORT)
