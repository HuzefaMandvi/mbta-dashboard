from datetime import date, datetime
from flask import Flask
from flask_table import Table, Col
import requests

app = Flask(__name__)

# https://api-v3.mbta.com/predictions?filter[stop]=place-north&filter[route_type]=2&direction_id=0&sort=-departure_time

api_url_base = "https://api-v3.mbta.com"
api_url_predictions = api_url_base + "/predictions"
api_url_schedule = api_url_base + "/schedules"
params_predictions = {'filter[stop]':'place-north', 'filter[route_type]':'2', 'direction_id':'0', 'sort':'-departure_time'}
params_schedule = {'filter[stop]':'place-north', 'filter[route_type]':'2', 'direction_id':'0', 'sort':'departure_time'}

class ItemTable(Table):
    border = True
    route_name = Col('Route')
    departure_time = Col('Departure')
    status = Col('Status')

#TODO - rename this class
class Item(object):
    def __init__(self, name, time, status):
        self.route_name = name
        self.departure_time = time
        self.status = status

def convert_timestamp_to_ampm(timestring):
    # get rid of UTC offset
    timestring = timestring[:-6]
    # convert 24hr time to AM/PM time
    d = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S")
    return d.strftime("%I:%M %p")

@app.route("/")
def hello_world():
    items = []
    item_counter = 0

    # first, try to get 10 live predictions
    r = requests.get(url=api_url_predictions, params=params_predictions)
    data = r.json()
    for item in data["data"][0:9]:
        route_departure_time = item["attributes"]["departure_time"]
        # if there is no departure time listed on a prediction, it is not valid
        if route_departure_time is not None:
            item_counter += 1
            route_name = item["relationships"]["route"]["data"]["id"]
            route_departure_time = convert_timestamp_to_ampm(route_departure_time)
            route_status = item["attributes"]["status"]
            route = Item(route_name, route_departure_time, route_status)
            items.append(route)

    # fill in the rest of the table with scheduled routes
    r = requests.get(url=api_url_schedule, params=params_schedule)
    data = r.json()
    # get current hour in HH:MM form in order to bound our schedule request
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    params_schedule["filter[min_time]"] = current_time
    for item in data["data"][item_counter:9]:
        route_name = item["relationships"]["route"]["data"]["id"]
        route_status = "Scheduled"
        route_departure_time = convert_timestamp_to_ampm(item["attributes"]["departure_time"])
        route = Item(route_name, route_departure_time, route_status)
        items.append(route)

    table = ItemTable(items)
    return table.__html__()