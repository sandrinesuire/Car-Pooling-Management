from django.shortcuts import render
from django.http import HttpResponse ,Http404
from django.template import loader
from django.shortcuts import render , get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView , UpdateView , DeleteView
from django.http import JsonResponse
from rider.models import ride
from django.core import serializers

import numpy as np
import googlemaps 
import json


def driverHome(request):
	print(request.user.username)	
	return render(request , "driverHome.html" , {'username' : request.user.username})

def driverInfo(request):
	print(request.user.username + " driveInfo")
	print(request.POST['destination'])
	return render(request , "driverProcess1.html" , {'username' : request.user.username , 'dest' : request.POST['destination']})

def searchRider(request):
	print("*******************&&&&&&&&&&&&&&&&&&&&&&&&&&&**********************")
	print(request)
	driverId = request.GET['id']
	liveLat = request.GET['liveLat']
	liveLong = request.GET['liveLong']
	driver_dest = request.GET['destination']
	print(liveLat + "++++++" + liveLong);
	print(request.GET['destination'])
	print("*******************&&&&&&&&&&&&&&&&&&&&&&&&&&&**********************")

	if liveLat == "" or liveLong == "":
		return JsonResponse({'success': False})

	riderSet = ride.objects.select_for_update().filter(status = False , complete = False)
	rideList = []

	gmaps = googlemaps.Client(key='AIzaSyB64EM3P7XmfNlop7aUjzacIXAQJVAMjkA') 
	for r in riderSet:
		print(type(r))
		print(r)
		my_dist = gmaps.distance_matrix((float(liveLat) ,float(liveLong)) , r.pickUp)['rows'][0]['elements'][0]["distance"]["value"]
		my_dist = my_dist/1000.0
		my_dist_1 = gmaps.distance_matrix(driver_dest , r.destination)['rows'][0]['elements'][0]["distance"]["value"]
		my_dist_1 = my_dist_1/1000.0
		print("the distance is " + str(my_dist))
		if my_dist < 20 and my_dist_1 < 20:
			data_dict = {'riderId':r.userId , 'pickUp': r.pickUp , 'destination' : r.destination}
			rideList.append(data_dict)

	#rideList = json.dumps(rideList)
	return JsonResponse({'rideList': rideList})
	#algo rider search 

	#[{"model": "rider.ride", "pk": "lodhuji", "fields": {"pickUp": "Bhopal Railway Station, Bajariya, Navbahar Colony, Bhopal, Madhya Pradesh, India", "destination": "New Delhi, Delhi, India", "complete": false, "status": false, "cost": 0}}]

def acceptRider(request):
	print(request)
	print("***************************")
	idList = request.GET['id']
	ind = idList.find("&&&----&&&")
	driverId = idList[:ind]
	riderId = idList[ind+10: ]
	print(driverId)
	print(riderId)
	success =  ride.acceptRide(riderId , driverId)
	acceptedSet = ride.objects.select_for_update().filter(status = True , driverId = driverId , complete = False)
	acceptList = []

	for r in acceptedSet:
		print(r)
		data_dict = {'riderId':r.userId , 'pickUp': r.pickUp , 'destination' : r.destination}
		acceptList.append(data_dict)
	
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	print(acceptList)
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	return JsonResponse({'success' : success , 'acceptList' : acceptList})


#<WSGIRequest: GET '/driver/accept?riderId=lodhuji&driverId=User01'>
#<WSGIRequest: GET '/driver/driveProcess?id=User01&liveLat=19.7514798&liveLong=75.7138884&destination=New%20Delhi%20Railway%20Station%2C%20Kamla%20Market%2C%20Ajmeri%20Gate%2C%20New%20Delhi%2C%20Delhi%2C%20India'>

def endRide(request):
	idList = request.GET['id']
	ind = idList.find("&&&----&&&")
	driverId = idList[:ind]
	riderId = idList[ind+10: ]
	print(driverId)
	print(riderId)
	r = get_object_or_404(ride, pk=riderId)
	r.complete = True
	cost = r.cost = np.random.randint(low=50, high=200)
	r.save()

	acceptedSet = ride.objects.select_for_update().filter(status = True , driverId = driverId , complete = False)
	acceptList = []

	for r in acceptedSet:
		print(r)
		data_dict = {'riderId':r.userId , 'pickUp': r.pickUp , 'destination' : r.destination}
		acceptList.append(data_dict)

	print(acceptList)
	print("------------------------------------------------- "+str(cost) + " ----------------------------------------------")
	return JsonResponse({'success' : True , 'acceptList' : acceptList, 'cost' : cost})
	

