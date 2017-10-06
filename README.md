# Pulse

![Pulse heart rate data display](http://i.imgur.com/nEIUO6x.png)

Just a little learning experiment for me to learn how to use OAuth 2, Python & the Fitbit API (and how those all come together) Definitely not ready for production. Fitbit's [Charge 2](https://www.fitbit.com/en-ca/charge2) tracks heart rate all day. I just used their [intraday time series endpoint](https://dev.fitbit.com/docs/heart-rate/#get-heart-rate-intraday-time-series) to sync heart rate data between a database on my computer and their servers, and display it nicely on a little website. 

## Requirements:

* Python 3.5+
* [requests](https://pypi.python.org/pypi/requests/)
* [requests-oauthlib](https://pypi.python.org/pypi/requests-oauthlib/0.8.0)
* [peewee](https://pypi.python.org/pypi/peewee/2.8.7)
* [Flask](http://flask.pocoo.org)
* [Chart.js](http://www.chartjs.org) for the beautiful graphs

## Trying it out:

Register an app over at [Fitbit](https://dev.fitbit.com). Make sure you set the 'OAuth 2.0 Application Type' to 'Personal'. The callback URL can be whatever you want if you're planning on just running this locally (it's not secure enough to actually run on a production server -- access tokens are stored as plaintext and the authorization flow is not appropriate for anything other than running it locally) Make note of your client ID. 

Get all the dependencies downloaded:

	pip install -r requirements.txt

Set the environment variable `'FITBIT_CLIENT_ID'` to whatever your client ID was from Fitbit, and set `'PULSE_KEY'` to a random string. Also, at the top of *app.py*:

```
fullname = 'Matthew Mascioni'
```

Change that to your name ;p The first time you run the script, it'll associate your name with an access token from Fitbit to access your data. The name isn't all that important. Based on the other options, by default it'll run on port 8000. Feel free to change that. With that, just run *app.py*

	python app.py

The first time you run it, the app will authenticate you via the Implicit Grant flow, obtaining an access token which is stored in the database for future use (another reason why it isn't production ready) Follow the steps in the command line. If all goes well, head over to `http://localhost:8000` (or whatever port you specified) and data for the today's date should be loaded up. To view any other date, follow the `http://localhost:8000/hr/year/month/day` pattern.

Enjoy :)