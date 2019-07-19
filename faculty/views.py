from django.shortcuts import render, HttpResponseRedirect,HttpResponse
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift,MakeupLecture,Year, Division, Room,IA, GuestLecture, OD
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import DurationField, F, ExpressionWrapper
import time
import json
from django.core import serializers
from django.core.files.storage import default_storage
import os
from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# # Update leave as approved by HOD
# def update_leave(request, leave_id):
#     Leave.objects.filter(id=leave_id).update(is_approved=True)
#     return HttpResponseRedirect('/hod/')

@login_required
def index(request):
	if not request.user.is_superuser and not request.user.is_staff:
		ias = IA.objects.filter(ia_date__gte = datetime.datetime.now())
		makeup_lecs = MakeupLecture.objects.filter(lec_date__gte = datetime.datetime.now())
		guest_lecs = GuestLecture.objects.filter(lec_date__gte = datetime.datetime.now())
		context_data = {
			"ias" : ias,
			"makeup_lecs" : makeup_lecs,
			"guest_lecs" : guest_lecs,
		}
		return render(request,"faculty/faculty_index.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def create_leave(request):
	if not request.user.is_superuser and not request.user.is_staff:
		return render(request,"faculty/leave_request.html",{})
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def submit_leave(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if request.method == 'POST':
			user = User.objects.get(pk = request.user.id)
			start_date_val = request.POST.get('leave_start_date')
			end_date_val = request.POST.get('leave_end_date')
			duration = request.POST.get('duration')
			start_time_val = ''
			end_time_val = ''
			if(duration == 'full'):
				start_time_val = '10:30'
				end_time_val = '17:15'
			elif(duration == 'first_half'):
				start_time_val = '10:30'
				end_time_val = '01:15'
			elif(duration == 'second_half'):
				start_time_val = '01:15'
				end_time_val = '17:15'
			else:
				return HttpResponse("Contact Admin")
			start_date_time = start_date_val + 'T' + start_time_val
			end_date_time = end_date_val + 'T' + end_time_val
			# Python date time objects
			start_date = datetime.datetime.strptime(start_date_time, '%m/%d/%YT%H:%M')
			end_date = datetime.datetime.strptime(end_date_time, '%m/%d/%YT%H:%M')
			lecs = Lecture.objects.filter(lec_day__id__in = range(start_date.weekday(),end_date.weekday()+1)).filter(taken_by = user).filter(lec_time__start_time__gte = datetime.datetime.time(start_date)).filter(lec_time__end_time__lte = datetime.datetime.time(end_date))
			adjust_opts = dict()
			new_leave = Leave.objects.get_or_create(leave_taken_by = user,leave_start_date=start_date.date(),leave_end_date = end_date.date(),leave_start_time=start_date.time(),leave_end_time = end_date.time())
			# print("####",new_leave)
			for lec in lecs:
				adjust_opts[lec] = User.objects.exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time)])
			# print(adjust_opts)
			context_data ={
				"start_date" : start_date_val,
				"end_date" : end_date_val,
				"start_time" : start_time_val,
				"end_time" : end_time_val,
				"lecs" : lecs,
				"adjust_opts" : adjust_opts,
				"leave_id" : new_leave[0].id
			}

			return render(request,"faculty/leave_request.html",context_data)
			# LoadShift.objects.create()
		return HttpResponse("Not logged in")
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def submit_load_shift(request):
	if not request.user.is_superuser and not request.user.is_staff:
		user = User.objects.get(pk = request.user.id)
		load_shifts = LoadShift.objects.filter(to_faculty = user)
		if request.method == 'POST':
			# print(request.POST)
			if(request.POST.get('leave_id')):
				leave = Leave.objects.get(pk = request.POST.get('leave_id'))
				# print(leave)
				# print(request.POST.getlist('lecture_id'))
				if(request.POST.getlist('lecture_id')):
					for faculty_id,lec_id in zip(request.POST.getlist('faculty_id'), request.POST.getlist('lecture_id')):
						l = LoadShift.objects.get_or_create(leave = leave,to_faculty = User.objects.get(pk = faculty_id),for_lecture = Lecture.objects.get(pk = lec_id))
						# Email notificaion

						subject = 'New Load Shift request'
						message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)

						message_data = {
							'loadshift' : l[0],
						}

						email_from = settings.EMAIL_HOST_USER
						recipient_list = []
						recipient_list.append(User.objects.get(pk = faculty_id).email)
						html_content = render_to_string('email/loadshift_notification.html', message_data,request) # render with dynamic value
						text_content = strip_tags(html_content)

						msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
						msg.attach_alternative(html_content, "text/html")
						# print(l[0].for_lecture)
						msg.send()
						# return render(request,'email/loadShift_notification.html', message_data)

		# send_mail(subject, message, email_from, recipient_list,fail_silently = False)

			else:
				html_error_data = {
					"error_code" : "404",
					"error_message" : "Loadshifts not found. Try again."
				}
				return render(request,"error.html",html_error_data)
			# print(user.username)
			# print(for_lec)
			# print(to_faculty)
		return render(request,"faculty/loadshift.html",{"load_shifts":load_shifts})
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

def email_accept_loadshift(request):
	if request.method == 'POST':
		load_shift = LoadShift.objects.get(pk = request.POST.get('load_shift'))
		# print(load_shift.id)
		if '_reject' in request.POST:
			load_shift.delete()
		elif '_approve' in request.POST:
			load_shift.approved_status = True
			load_shift.save()
		return True

@login_required
def view_load_shifts(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if request.method == 'POST':
			load_shift = LoadShift.objects.get(pk = request.POST.get('load_shift'))
			if '_reject' in request.POST:
					load_shift.delete()
			elif '_approve' in request.POST:
					load_shift.approved_status = True
					load_shift.save()

		user = User.objects.get(pk = request.user.id)
		load_shifts = LoadShift.objects.filter(to_faculty = user)

		return render(request,"faculty/loadshift.html",{"load_shifts":load_shifts})
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def get_makeup(request):
	if not request.user.is_superuser and not request.user.is_staff:
		days = DaysOfWeek.objects.all().exclude(day_name__in = ('Sunday','Saturday'))
		m_lecs = MakeupLecture.objects.filter(lec_date__lte = datetime.datetime.now()+datetime.timedelta(days = 7))
		# print("$#$#$#",m_lecs)
		years = Year.objects.all()
		divions = Division.objects.all()
		subjects = Subject.objects.all()
		timeslots = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff__lte= datetime.timedelta(hours = 1))


		free = dict()

		for day in days:
			# print(day.id)
			# m_lecs = MakeupLecture.objects.filter(lec_date__week_day = day.id)
			free_ts = list()
			for timeslot in timeslots:
				if(not(Lecture.objects.filter(lec_day = day,lec_time = timeslot).exists()) and not (MakeupLecture.objects.filter(lec_date__week_day = (day.id + 1),lec_time = timeslot).exists())):
					free_ts.append(timeslot)

			free[day] = free_ts
		# print(free)

		context_data = {
			"free_slots" : free,
			"years" : years,
			"subjects" : subjects,
			"divisions" : divions
		}

		return render(request,"faculty/makeup.html",context_data)

	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def post_makeup(request):
	if not request.user.is_superuser and not request.user.is_staff:
		success = False
		if(request.method == "POST"):
			# print(request.POST)
			year = Year.objects.get(pk = int(request.POST.get('year')))
			subject = Subject.objects.get(pk = int(request.POST.get('subject')))
			division = Division.objects.get(pk = int(request.POST.get('division')))
			date = datetime.datetime.strptime(request.POST.get('makeup_date'),'%m/%d/%Y')
			timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
			room = Room.objects.get(pk = int(request.POST.get('locations')))
			user = User.objects.get(pk = request.user.id)
			# print(year,"--",subject,"--",division,"--",date,"--",timeslot)
			makeup_lec = MakeupLecture(year = year, lec_subject = subject, division = division,lec_date = date, lec_time = timeslot, lec_taken_by = user, lec_in=room)
			try:
				makeup_lec.full_clean()
				makeup_lec.save()
				context_data = {
					"success" : 'true'
				}
			except Exception as e:
				print("Cannnot save",e)
				context_data = {
					"errors" : e ,
				}

			return render(request,"faculty/makeup.html",context_data)
		else:
			return HttpResponseRedirect('./')

	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)


# def get_subjects(request,yid):
	# print("request")
# 	try:
# 		year = Year.objects.get(pk = yid)
# 		subjects = Subject.objects.filter(year = year)
		# print(subjects)
# 	except:


# 	return HttpResponse("<h1>Test</h1>")

@login_required
def get_timeslots(request,syear,sdate):
	# print(syear)
	# print(sdate)
	if not request.user.is_superuser and not request.user.is_staff:
		if(syear!='-1'):
			year = Year.objects.get(pk = int(syear))
			date = datetime.datetime.strptime(sdate,'%Y-%m-%d')
			day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
			lecs = Lecture.objects.filter(lec_day = day,lname__year = year)
			# print(lecs)
			makeup_lecs = MakeupLecture.objects.filter(lec_date = date,year = year)
			# print(makeup_lecs)
			ias = IA.objects.filter(ia_date = date, ia_year =year)
			guest_lecs = GuestLecture.objects.filter(lec_date = date,lec_year = year)
			timeslots = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff__lte= datetime.timedelta(hours = 2))
			# print(timeslots)
			# occupied_rooms = list()
			free_ts = list()
			for timeslot in timeslots:

				filtered_lecs = lecs.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time)

				filtered_makeup_lecs = makeup_lecs.filter(lec_time__start_time__gte = timeslot.start_time,lec_time__end_time__lte = timeslot.end_time)

				filtered_ia = ias.filter(ia_time__start_time__gte = timeslot.start_time,ia_time__end_time__lte = timeslot.end_time)

				filtered_guest_lecs = guest_lecs.filter(lec_time__start_time__gte = timeslot.start_time,lec_time__end_time__lte = timeslot.end_time)

				if(not filtered_lecs.exists() and not filtered_makeup_lecs.exists() and not filtered_ia.exists() and not filtered_guest_lecs.exists()):
					free_ts.append(timeslot)
			# print(lecs)
			# print(makeup_lecs)
			ts_json = serializers.serialize("json",free_ts)

			# rooms_json = serializers.serialize("json",occupied_rooms)

			# data_json = {
			# 	"timeslots" : ts_json,
			# 	"rooms" : rooms_json
			# }
			# print(ts_json)
			return HttpResponse(ts_json)
		else:
			return HttpResponse("Select Year")
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def get_available_rooms(request,sdate,slot):
	# print(sdate)
	# print(slot)
	if not request.user.is_superuser and not request.user.is_staff:
		if(slot!='-1'):
			date = datetime.datetime.strptime(sdate,'%Y-%m-%d')
			day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
			timeslot = TimeSlot.objects.get(pk = int(slot))
			lecs = Lecture.objects.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time,lec_day = day)
			makeup_lecs = MakeupLecture.objects.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time,lec_date = date)
			ias = IA.objects.filter(ia_date = date, ia_time__start_time__gte = timeslot.start_time,ia_time__end_time__lte = timeslot.end_time)
			guest_lecs = GuestLecture.objects.filter(lec_date = date, lec_time__start_time__gte = timeslot.start_time,lec_time__end_time__lte = timeslot.end_time)
			occupied_rooms = list()
			for lec in lecs:
				occupied_rooms.append(lec.lec_in)
			for lec in makeup_lecs:
				occupied_rooms.append(lec.lec_in)
			for ia in ias:
				occupied_rooms.append(ia.ia_in)
			for lec in guest_lecs:
				occupied_rooms.append(lec.lec_in)

			rooms = Room.objects.exclude(room__in = occupied_rooms)
			rooms_json = serializers.serialize("json",rooms)
			return HttpResponse(rooms_json)
		else:
			return HttpResponse("Select TimeSlot")
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def get_ia(request):
	if not request.user.is_superuser and not request.user.is_staff:
		years = Year.objects.all()
		subjects = Subject.objects.all()

		context_data = {
			"years" : years,
			"subjects" : subjects
		}

		return render(request,"faculty/ia.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def post_ia(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if(request.method == 'POST'):
			# print(request.POST)
			year = Year.objects.get(pk = int(request.POST.get('year')))
			subject = Subject.objects.get(pk = int(request.POST.get('subject')))
			date = datetime.datetime.strptime(request.POST.get('ia_date'),'%m/%d/%Y')
			timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
			room = Room.objects.get(pk = int(request.POST.get('locations')))

			try:
				ia = IA(ia_year = year, ia_subject = subject,ia_date = date,ia_time = timeslot,ia_in = room)
				ia.full_clean()
				# print(ia)
				ia.save()

				context_data = {
					"success" : 'true'
				}

			except Exception as e:

				context_data = {
					"errors" : e
				}

			return render(request,"faculty/ia.html",context_data)
		else:
			return HttpResponseRedirect('./')
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def guestlecture(request):
	if not request.user.is_superuser and not request.user.is_staff:
		years = Year.objects.all()
		subjects = Subject.objects.all()

		context_data = {
			"years" : years,
			"subjects" : subjects
		}

		return render(request,"faculty/guestlecture.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)


@login_required
def guestlecture_schedule(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if(request.method == 'POST'):
			# print(request.POST)
			year = Year.objects.get(pk = int(request.POST.get('year')))
			subject = Subject.objects.get(pk = int(request.POST.get('subject')))
			date = datetime.datetime.strptime(request.POST.get('guestlec_date'),'%m/%d/%Y')
			timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
			room = Room.objects.get(pk = int(request.POST.get('locations')))

			try:
				guest_lecture = GuestLecture(lec_year = year, lec_subject = subject,lec_date = date,lec_time = timeslot,lec_in = room)
				guest_lecture.full_clean()
				# print(guest_lecture)
				guest_lecture.save()

				context_data = {
					"success" : 'true'
				}

			except Exception as e:

				context_data = {
					"errors" : e
				}

			return render(request,"faculty/guestlecture.html",context_data)
		else:
			return HttpResponseRedirect('./')
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def od(request):
	if not request.user.is_superuser and not request.user.is_staff:
		context_data = {}
		return render(request,"faculty/od.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def submit_od(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if(request.method == 'POST'):
			od_type = request.POST.get('od-type')
			title = request.POST.get('title')
			og_details = request.POST.get('og-details')
			supporting_og = request.POST.get('Supporting-og')
			from_date = datetime.datetime.strptime(request.POST.get('from_date'),'%m/%d/%Y')
			to_date = datetime.datetime.strptime(request.POST.get('to_date'),'%m/%d/%Y')
			last_date = datetime.datetime.strptime(request.POST.get('last_date'),'%m/%d/%Y')
			fees = request.POST.get('fees')
			# print(request.FILES)
			correspondence_filename = request.FILES[u'correspondence'].name
			correspondence_file = request.FILES['correspondence']
			taken_by = request.user
			# with default_storage.open('od/correspondence/'+correspondence_filename,'wb+') as destination:
			# 	for chunk in correspondence_file.chunks():
			# 		destination.write(chunk)

			# print(settings.MEDIA_ROOT)

			# # file = open(correspondence_file)
			# path = os.path.join(settings.MEDIA_ROOT,'od','correspondence',correspondence_filename)
			# file = open(path,'wb+')

			scope = request.POST.get('scope')

			new_od = OD(od_type = od_type, od_title = title, od_details = og_details, supporting_organisation = supporting_og, from_date = from_date, to_date = to_date, last_date = last_date, fees = fees,scope = scope, taken_by = taken_by)
			new_od.correspondence.save(correspondence_filename,correspondence_file)
			new_od.save()

			lecs = Lecture.objects.filter(lec_day__id__in = range(from_date.weekday(),to_date.weekday()+1)).filter(taken_by = taken_by)
			# print(lecs)
			adjust_opts = dict()
			for lec in lecs:
				adjust_opts[lec] = User.objects.exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time)])
			# print(adjust_opts)

			context_data = {
				"adjust_opts" : adjust_opts,
				"od" : new_od
			}

			# print(request.POST)

			return render(request,"faculty/od.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def submit_od_loadshift(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if(request.method == 'POST'):
			# print(request.POST)
			if(request.POST.get('od_id')):
				od = OD.objects.get(pk = request.POST.get('od_id'))
				# print(request.POST.getlist('lecture_id'))
				if(request.POST.getlist('lecture_id')):
					for faculty_id,lec_id in zip(request.POST.getlist('faculty_id'), request.POST.getlist('lecture_id')):
						l = LoadShift.objects.get_or_create(od = od,to_faculty = User.objects.get(pk = faculty_id),for_lecture = Lecture.objects.get(pk = lec_id))

						# Email notificaion

						subject = 'New Load Shift request'
						message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)

						message_data = {
							'loadshift' : l[0],
						}

						email_from = settings.EMAIL_HOST_USER
						recipient_list = []
						recipient_list.append(User.objects.get(pk = faculty_id).email)
						html_content = render_to_string('email/loadshift_notification.html', message_data,request) # render with dynamic value
						text_content = strip_tags(html_content)

						msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
						msg.attach_alternative(html_content, "text/html")
						# print(l[0].for_lecture)
						msg.send()

					context_data = {
						"success" : 'true',
					}
			else:
				context_data = {
					"errors" : "Contact Admin"
	 			}
				# print("No load shifts")
			return render(request,"faculty/od.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def send_email(request):
	if not request.user.is_superuser and not request.user.is_staff:
		subject = 'Test Mail'
		message = 'This is a test mail from admin'
		email_from = settings.EMAIL_HOST_USER
		recipient_list = ['harshal.pm@somaiya.edu',]
		html_content = render_to_string('email/loadShift_notification.html', {'varname':'value'}) # render with dynamic value
		text_content = strip_tags(html_content)

		msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
		msg.attach_alternative(html_content, "text/html")

		msg.send()
		# return render(request,'email/loadshift.html',{})
		return HttpResponse("Success")
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

