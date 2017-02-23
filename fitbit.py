# Import some stuff
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient

class FitbitClient(object):

	def __init__(self, client_id, token, scope=["activity", "heartrate", "location", "nutrition", "profile", "settings", "sleep", "social", "weight"]):
		"""Initializes the Fibit client. Specify the client_id and client_secret if you're creating a token for the first time. Otherwise, pass in the token.
		The class automatically asks for a full scope. You can change this by passing in a list with your desired scope.
		
		Note: The OAuth code is based off a modified version of the example in this issue: https://github.com/requests/requests-oauthlib/issues/104
		(thank you!)

		"""
		
		print("Access token passed in: {}".format(token['access_token']))

		if token['access_token'] == "":
			# We need to fetch a token for the user.
			print("Note: no token was passed in.")

			self.client = MobileApplicationClient(client_id)
			self.fitbit = OAuth2Session(client_id, client=self.client, scope=scope)

			authorization_base_url = "https://www.fitbit.com/oauth2/authorize"

			authorization_url, state = self.fitbit.authorization_url(authorization_base_url, access_type="offline", approval_prompt="force")

			print("Authorization URL: {}".format(authorization_url))

			raw_callback_url = input("Paste callback here: ")

			self.fitbit.token_from_fragment(raw_callback_url)
			self.token = self.fitbit.token['access_token']

			print(self.fitbit.token)

		else:
			# We've got an access token, and we'll use it.
			self.client = MobileApplicationClient(client_id)
			self.fitbit = OAuth2Session(client_id, client=self.client, scope=scope, token=token)
			self.token = token['access_token']


