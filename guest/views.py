from django.shortcuts import render
from faculty.models import Room
from django.http import JsonResponse
import datetime
from . models import Reservation
from datetime import timedelta


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
		if request.method == 'POST':
			room = Room.objects.get(pk = request.POST.get('room_id'))
			institute = request.POST.get('institute').upper()
			department = request.POST.get('department')
			purpose = request.POST.get('purpose')
			start_date = datetime.datetime.strptime(request.POST.get('start_date'),'%m/%d/%Y')
			end_date = datetime.datetime.strptime(request.POST.get('end_date'),'%m/%d/%Y')
			start_time = datetime.datetime.strptime(request.POST.get('start_time'),'%H:%M').time()
			end_time = datetime.datetime.strptime(request.POST.get('end_time'),'%H:%M').time()
			contact_person = request.POST.get('contact_person')
			email = request.POST.get('email')
			try:
				r = Reservation.objects.get_or_create(room = room,institute = institute,department = department,purpose = purpose,start_date = start_date,end_date = end_date,start_time = start_time,end_time = end_time,contact_person = contact_person,email = email)
				context_data = {
					"success" : True,
				}
			except Exception as e:
				context_data = {
					"errors" : e,
				}
			return render(request,"guest/guest_reserve.html",context_data)
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
			# print(request.POST.get('date'))
			start_date = datetime.datetime.strptime(request.POST.get('start_date'),'%m/%d/%Y')
			end_date = datetime.datetime.strptime(request.POST.get('end_date'),'%m/%d/%Y')
			busy_timeslots = list()
			# print(start_date)
			# print(end_date)
			# print(Reservation.objects.filter(start_date__lte = end_date,end_date__gte = start_date))
			for reservation in Reservation.objects.filter(start_date__lte = end_date,end_date__gte = start_date):
				
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

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def events(request):
	if not request.user.is_authenticated:
		if request.method == 'POST':
			events = list()
			for reservation in Reservation.objects.all():

				for date in daterange(reservation.start_date,reservation.end_date):
					event_details = {
						'eventName' : reservation.purpose + " (" + reservation.start_time.strftime('%I:%M %p') +" to "+ reservation.end_time.strftime('%I:%M %p') + ")",
						'calendar' : 'Other',
						'color' : 'green' if reservation.approved_status else 'orange',
						'date' : date.strftime('%d/%m/%Y'),
						'calendar' : 'Accepted' if reservation.approved_status else 'Pending',
					}
					events.append(event_details)
				# { eventName: 'IOT Seminar', calendar: 'Other', color: 'green', date: '15/08/2019'}
			json_data = {
				'status' : 'success',
				'events' : events 
			}
			return JsonResponse(json_data)
		return render(request,"guest/view_events.html",{})

	json_data = {
		'status' : 'false',
		'message' : 'UNAUTHORIZED'
	}
	return JsonResponse(json_data, status=500)