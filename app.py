from fitbit import FitbitClient
from helper import Rainbow, Helper
from flask import Flask, render_template, flash, url_for, redirect, g
import models, exceptions
import requests
import os, sys, datetime

client_id = os.environ["FITBIT_CLIENT_ID"]
DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = os.environ["PULSE_KEY"]

@app.before_request
def before_request():
	"""Connect to database before each request."""
	g.db = models.DATABASE
	g.db.connect()

@app.after_request
def after_request(response):
	"""Close database connection afterwards."""
	g.db.close()
	return response

@app.teardown_request
def teardown_request(exception):
	if exception:
		print(exception)
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

def sync_day_to_database(date=datetime.date.today()):
	# Grab a summary of the day, with heart rate data, from Fitbit
	try:
		summ, intraday = fitbit_client.fetch_heartrate_detailed_day(date=date)

		# Add a new day to our database (or retrieve it)
		date_to_pass = Helper.string_to_datetime(summ['date'], 'date')
		retr = models.Day.create_day(human, date_to_pass)

		# Update resting heart rate for that day, if one wasn't available previously.
		if retr.resting_hr != summ['resting_rate']:
			retr.update_resting_hr(summ['resting_rate'])

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
		print("About to add {} new heart rates.".format(len(delta)))
		models.HeartRate.import_rates(day, delta)

@app.route("/")
def index():
	today = datetime.date.today()
	return redirect(url_for('display_hr_data', year=today.year, month=today.month, day=today.day))

@app.route("/hr/<int:year>/<int:month>/<int:day>")
def display_hr_data(year, month, day):
	try:
		retrieved_day = models.Day.get_day(datetime.date(year=year, month=month, day=day))
	except:
		sync_day_to_database(datetime.date(year=year, month=month, day=day))
		retrieved_day = models.Day.get_day(datetime.date(year=year, month=month, day=day))

	return render_template('display_hr.html', retrieved_day=retrieved_day)

@app.route("/hr/sync/<int:year>/<int:month>/<int:day>")
def sync_hr_data(year, month, day):
	if year and month and day:
		try:
			sync_day_to_database(datetime.date(year=year, month=month, day=day))
		except Exception as e:
			print("{} Unexpected error: {}{}".format(Rainbow.red, e, Rainbow.endc))
			flash("Could not sync to Fitbit.", 'error')
		return redirect(url_for('display_hr_data', year=year, month=month, day=day))	
	else:
		return redirect(url_for('index'))


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
