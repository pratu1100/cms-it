from django.shortcuts import render
from faculty.models import Room
from django.http import JsonResponse
import datetime
from . models import Reservation

# Create your views here.
def index(request):
	if not request.user.is_authenticated:
		return render(request,"guest/guest_index.html",{})
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

def reserve(request):
	if not request.user.is_authenticated:
		rooms = Room.objects.filter(room = "B507")
		context_data = {
			"rooms" : rooms,
		}
		return render(request,"guest/guest_reserve.html",context_data)

	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

def get_timeslots(request):
	if not request.user.is_authenticated:
		if request.method == 'POST':
			print(request.POST.get('date'))
			date = datetime.datetime.strptime(request.POST.get('date'),'%m/%d/%Y')
			busy_timeslots = list()
			for reservation in Reservation.objects.filter(date = date):
				timeslot = list() 
				timeslot.append(reservation.start_time.strftime("%H:%M"))
				timeslot.append(reservation.end_time.strftime("%H:%M"))
				busy_timeslots.append(timeslot)
			json_data = {
				'status' : 'success',
				'timeslots' : busy_timeslots,
			}
			return JsonResponse(json_data)
	json_data = {
		'status' : 'false',
		'message' : 'UNAUTHORIZED'
	}
	return JsonResponse(json_data, status=500)