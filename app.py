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

try:
	summ, intraday = fitbit_client.fetch_heartrate_intraday(date=datetime.date(year=2017, month=2, day=25))
except (exceptions.InputError, ValueError):
	pass

for sample in intraday:
	print("{} \t{}".format(sample['time'], sample['value']))