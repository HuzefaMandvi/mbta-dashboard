from os import readlink
from flask import Flask
import requests

app = Flask(__name__)

# https://api-v3.mbta.com/predictions?filter[stop]=place-north&filter[route_type]=2&direction_id=0&sort=-departure_time

api_url_base = "https://api-v3.mbta.com"
api_url_predictions = api_url_base + "/predictions"
api_url_schedule = api_url_base + "/schedules"
params = {'filter[stop]':'place-north', 'filter[route_type]':'2', 'direction_id':'0', 'sort':'-departure_time'}

@app.route("/")
def hello_world():
    r = requests.get(url=api_url_predictions, params=params)
    data = r.json()
    return data["data"][0]["relationships"]["route"]["data"]["id"]