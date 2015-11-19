from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
# import urllib.request
import json
import requests

api_url= 'http://tracker.wallinginfosystems.com/api/v1/'
# api_url='http://yeahthattrolley.azurewebsites.net/api/v1/' 

# Create your views here.
@xframe_options_exempt
def track(request):
	#get the list of currently active routes
	activeroutes = requests.get(api_url + "Routes/Active").json()
	routes = []

	#get the list of schedules in case there's no trolleys running
	schedules = requests.get(api_url + "RouteSchedules").json()

	#sort schedules
	dayofweekorder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	schedules.sort(key=lambda x: (dayofweekorder.index(x['DayOfWeek']), int(x['StartTime'][0:2].replace(':', '')) + (0 if 'AM' in x['StartTime'] else 12), int(x['EndTime'][0:2].replace(':', '')) + (0 if 'AM' in x['EndTime'] else 12)), reverse=True)
	#this sorting quickly became pretty ugly.  I'm not returned clean datetimes from the API, so I'm replacing the first two of the time (hours, e.g. '4:' or '12') and adding 12 if it's PM.
	#using tuples to sort by day of week, then start time, then end time.

	#have to make this call too in order to get the names of the routes
	routenames = requests.get(api_url + "Routes").json()

	schedule = []
	for routeschedule in schedules:
		schedulename = "Route " + str(routeschedule['ID'])
		for route in routenames:
			if (route['ID'] == routeschedule['RouteID']):
				schedulename = route['LongName']
				break
		schedule.append('<b>' + schedulename + ":</b><br>" + str(routeschedule['DayOfWeek']) + " " + str(routeschedule['StartTime']) + " - " + str(routeschedule['EndTime']))

	for route in activeroutes:
		#get the route definition for each active route
		routes.append(requests.get(api_url + "Routes/" + str(route['ID'])).json())

	#get the active trolley data
	#trolleys = requests.get(api_url + "Trolleys").json()

	context = {
		'routes': json.dumps(routes),
		'schedule': json.dumps(schedule)
	}
	return render(request, 'trolleytracker/index.html', context)

@xframe_options_exempt
def update(request):
	activetrolleys = requests.get(api_url + "Trolleys/Running").json()
	trolleys = [requests.get(api_url + "Trolleys/" + str(trolley['ID'])).json() for trolley in activetrolleys]

	return HttpResponse(json.dumps(trolleys))
