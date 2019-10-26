from django.shortcuts import render,HttpResponseRedirect
from faculty.models import Leave
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from faculty.models import LoadShift,Leave, OD
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from guest.models import Reservation
import datetime
from datetime import timedelta
# Create your views here.
@login_required
def index(request):
	if request.user.is_superuser:
		return HttpResponseRedirect('/hod/approveleaves')
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def get_leaves(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			leave = Leave.objects.get(pk = request.POST.get('leave_id'))
			# default duration
			duration = 'full' 
			if(leave.leave_start_time.strftime("%H:%M") == '10:30' and leave.leave_end_time.strftime("%H:%M") == '17:15'):
				duration = 'full'
			elif(leave.leave_start_time.strftime("%H:%M") == '10:30' and leave.leave_end_time.strftime("%H:%M") == '13:15'):
				duration = 'first_half'
			elif(leave.leave_start_time.strftime("%H:%M") == '13:15' and leave.leave_end_time.strftime("%H:%M") == '17:15'):
				duration = 'second_half'
			else:
				duration = leave.leave_start_time.strftime("%H:%M") + " TO " + leave.leave_end_time.strftime("%H:%M")
			
			subject = 'Leave Notification'			
			message_data = {
				'leave' : leave,
				'duration' : duration
			}
			
			if '_reject' in request.POST:
				leave.approved_status = False;
				leave.save()
			elif '_approve' in request.POST:
				leave.approved_status = True
				leave.save() 

			subject = 'Leave Notification'
					
		

			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			recipient_list.append(leave.leave_taken_by.email)
			html_content = render_to_string('email/faculty/approve_leave.html', message_data) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
			
			msg.send()
			# return render(request,'email/faculty/approve_leave.html', message_data)

		leaves = Leave.objects.filter(approved_status = None)
		leave_loads_pairs = list()
		for leave in leaves:
			loads_data = list()
			loads = LoadShift.objects.filter(leave = leave)
			for load in loads:
				loads_data.append(load)
			leave_loads_pairs.append((leave,loads_data))

		context_data = {
			'leave_loads_pairs' : leave_loads_pairs
		}
		# print(context_data)

		return render(request, 'hod/leaves.html', context_data)

	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def leave_history(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			leave = Leave.objects.get(pk = request.POST.get('leave_id'))
			# default duration
			duration = 'full' 
			if(leave.leave_start_time.strftime("%H:%M") == '10:30' and leave.leave_end_time.strftime("%H:%M") == '17:15'):
				duration = 'full'
			elif(leave.leave_start_time.strftime("%H:%M") == '10:30' and leave.leave_end_time.strftime("%H:%M") == '13:15'):
				duration = 'first_half'
			elif(leave.leave_start_time.strftime("%H:%M") == '13:15' and leave.leave_end_time.strftime("%H:%M") == '17:15'):
				duration = 'second_half'
			else:
				duration = leave.leave_start_time.strftime("%H:%M") + " TO " + leave.leave_end_time.strftime("%H:%M")
			
			subject = 'Leave Notification'			
			message_data = {
				'leave' : leave,
				'duration' : duration
			}
			
			if '_reject' in request.POST:
				leave.approved_status = False;
				leave.save()
			elif '_approve' in request.POST:
				leave.approved_status = True
				leave.save() 		

			#-------------------TO REQUESTING FACULTY------------------- 
			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			recipient_list.append(leave.leave_taken_by.email)
			html_content = render_to_string('email/faculty/approve_leave.html', message_data) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
			
			msg.send()
			# return render(request,'email/faculty/approve_leave.html', message_data)
		leaves = Leave.objects.exclude(approved_status = None)
		leave_loads_pairs = list()
		for leave in leaves:
			loads_data = list()
			loads = LoadShift.objects.filter(leave = leave)
			for load in loads:
				loads_data.append(load)
			leave_loads_pairs.append((leave,loads_data))

		context_data = {
			'leave_loads_pairs' : leave_loads_pairs
		}
		return render(request,"hod/leave_history.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)


@login_required
def get_ods(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			od = OD.objects.get(pk = request.POST.get('od_id'))
			subject = 'OD Notification'			
			message_data = {
				'od' : od,
			}
			if '_reject' in request.POST:
				od.delete()	
			elif '_approve' in request.POST:
				od.approved_status = True
				od.save()

			#-------------------TO REQUESTING FACULTY------------------- 
			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			recipient_list.append(od.taken_by.email)
			html_content = render_to_string('email/faculty/approve_od.html', message_data) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
			
			msg.send()
			# return render(request,'email/faculty/approve_od.html', message_data)
		ods = OD.objects.filter(approved_status = None)
		od_loads_pairs = list()
		for od in ods:
			loads_data = list()
			loads = LoadShift.objects.filter(od = od)
			for load in loads:
				loads_data.append(load)
			od_loads_pairs.append((od,loads_data))

		context_data = {
			"od_loads_pairs" : od_loads_pairs,
		}
		return render(request, 'hod/approve_ods.html', context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

@login_required
def events(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			events = list()
			for reservation in Reservation.objects.all():
				if(reservation.approved_status):
					color = "green"
				else:
					color = "orange"
				for date in daterange(reservation.start_date,reservation.end_date):
					event_details = {
						'eventName' : reservation.purpose + " (" + reservation.start_time.strftime('%I:%M %p') +" to "+ reservation.end_time.strftime('%I:%M %p') + ")",
						'calendar' : 'Other',
						'color' : color,
						'date' : date.strftime('%d/%m/%Y')
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

@login_required
def room_reservations(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			event = Reservation.objects.get(pk = request.POST.get('event_id'))
			if '_reject' in request.POST:

				event.approved_status = False;
				event.save()
				
			elif '_approve' in request.POST:
			
				event.approved_status = True
				event.save() 

			subject = 'Room reservation Update'
					
			message_data = {
				'reservation' : event,
			}

			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			recipient_list.append(event.email)
			html_content = render_to_string('email/guest/event_approve_notification.html', message_data) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
			
			msg.send()

			# return render(request,'email/guest/event_approve_notification.html', message_data)

		events = Reservation.objects.filter(approved_status = None)
		context_data = {
			"events" : events,
		}
		return render(request,"hod/room_reservations.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)