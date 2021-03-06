# Import some stuff
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient
from helper import Rainbow

import datetime

class FitbitClient(object):

	def __init__(self, client_id, token, scope=["activity", "heartrate", "location", "nutrition", "profile", "settings", "sleep", "social", "weight"]):
		"""Initializes the Fibit client. Specify the client_id and client_secret if you're creating a token for the first time. Otherwise, pass in the token.
		The class automatically asks for a full scope. You can change this by passing in a list with your desired scope.
		
		Note: The OAuth code is based off a modified version of the example in this issue: https://github.com/requests/requests-oauthlib/issues/104
		(thank you!)
		"""

		if token['access_token'] == "":
			# We need to fetch a token for the user.
			print("Note: looks like we don't have an access token yet. Let's fetch one.")

			self.client = MobileApplicationClient(client_id)
			self.fitbit = OAuth2Session(client_id, client=self.client, scope=scope)

			authorization_base_url = "https://www.fitbit.com/oauth2/authorize"

			authorization_url, state = self.fitbit.authorization_url(authorization_base_url)

			print("Please go to the following authorization URL: {}".format(authorization_url))

			raw_callback_url = input("Paste callback URL you get back here: ")

			self.fitbit.token_from_fragment(raw_callback_url)
			self.token = self.fitbit.token['access_token']

			print(self.fitbit.token)

		else:
			# We've got an access token, and we'll use it.
			self.client = MobileApplicationClient(client_id)
			self.fitbit = OAuth2Session(client_id, client=self.client, scope=scope, token=token)
			self.token = token['access_token']


	def fetch_heartrate_detailed_day(self, date=datetime.date.today(), detail='1min'):
		"""Implementation of: https://dev.fitbit.com/docs/heart-rate/#get-heart-rate-intraday-time-series

		Note: Application needs to be of the 'Personal' type in order to access this.
		By default, this will fetch intraday series data for the current day, with a detail level of 1 min, for the entire day.
		You can pass '1sec' or '1min' to the detail argument."""

		if detail not in ['1min', '1sec']:
			print("You can only pass in '1min' or '1sec' as the detail argument. Leave blank for minute detail.")
			raise InputError
			
		date_to_pass = date.strftime('%Y-%m-%d')

		request = self.fitbit.get('https://api.fitbit.com/1/user/-/activities/heart/date/{}/1d/{}.json'.format(date_to_pass, detail))

		if request.status_code == 200:
			print(Rainbow.darkcyan+"Rate Limiting: {Fitbit-Rate-Limit-Remaining}/{Fitbit-Rate-Limit-Limit} API calls remaining. Limits reset in {Fitbit-Rate-Limit-Reset} seconds.".format(**request.headers)+Rainbow.endc)

			try:
				response_dictionary = request.json()

				try:
					resting_hr = response_dictionary['activities-heart'][0]['value']['restingHeartRate']
				except KeyError:
					# The views of our app will interpret this as 'Fitbit hasn't given an RHR yet', which is true.
					resting_hr = 0

				summary = {'date': response_dictionary['activities-heart'][0]['dateTime'],
							'resting_rate': resting_hr}

				intraday_series = response_dictionary['activities-heart-intraday']['dataset']

				return summary, intraday_series

			except ValueError:
				print(Rainbow.red+"Response wasn't valid JSON."+Rainbow.endc)
			except KeyError as ke:
				print(Rainbow.red+"{} could not be found in Fitbit's response dictionary.".format(ke)+Rainbow.endc)

			





		


