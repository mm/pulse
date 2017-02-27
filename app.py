from fitbit import FitbitClient
from helper import Rainbow, DatabaseHelper
import models
import requests
import os

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

r = fitbit_client.fitbit.get('https://api.fitbit.com/1/user/-/activities/heart/date/2017-02-22/1d/1min.json')

try:
	response_dictionary = r.json()
except ValueError:
	print("Response wasn't valid JSON.")

summary = {'date': response_dictionary['activities-heart'][0]['dateTime'],
			'resting_rate': response_dictionary['activities-heart'][0]['value']['restingHeartRate']}

print(summary)

intraday_access = response_dictionary['activities-heart-intraday']['dataset']

for sample in intraday_access:
	print("{} \t{}".format(sample['time'], sample['value']))