from django.shortcuts import render, HttpResponseRedirect,HttpResponse
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift,MakeupLecture,Year, Division, Room,IA, GuestLecture, OD, Batch, IaBatchRoomMapping, LeaveType
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
from itertools import chain
from EmailManager.views import send_async_mail

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
		print("######",guest_lecs)
		context_data = {
			"ias" : ias,
			"makeup_lecs" : makeup_lecs,
			"guest_lectures" : guest_lecs
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
		context_data = {
			"leave_types" : LeaveType.objects.all(),
		}
		return render(request,"faculty/leave_request.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)


def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + datetime.timedelta(n)

@login_required
def submit_leave(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if request.method == 'POST':
			user = User.objects.get(pk = request.user.id)
			leave_type = LeaveType.objects.get(pk = request.POST.get('leave_type'));
			# print(request.FILES)
			# print(leave_type)
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
			faculty_on_leave = [x.leave_taken_by.id for x in Leave.objects.filter(leave_start_date__lte = end_date,leave_end_date__gte = start_date).exclude(approved_status = True).exclude(approved_status = None)]
			faculty_on_od = [x.taken_by.id for x in OD.objects.filter(from_date__lte = end_date,to_date__gte = start_date).exclude(approved_status = True).exclude(approved_status = None)]
			new_leave = Leave.objects.get_or_create(leave_taken_by = user,leave_start_date=start_date.date(),leave_end_date = end_date.date(),leave_start_time=start_date.time(),leave_end_time = end_date.time(),leave_type = leave_type)
			# print("####",new_leave)
			# if medical leave
			if(new_leave[0].leave_type.id == 3):
				# print(new_leave[0].leave_type)
				# print(request.POST.get('supporting_file'))
				try:
					# print(new_leave[0])
					# uploaded_supporting_filename = request.POST.get('supporting_file')
				# pinrt(request.FILES['supporting_file'])
					uploaded_supporting_filename = request.FILES[u'supporting_file'].name
					uploaded_supporting_file = request.FILES['supporting_file']
					new_leave[0].supporting_file.save(uploaded_supporting_filename,uploaded_supporting_file)
					new_leave[0].save()
				except Exception as e:
					print(e)
					pass

			for date in daterange(start_date,end_date+datetime.timedelta(days=1)):
				# print(date,(date.weekday()+1)%7)\
				# days_in_duration.append((date.weekday()+1)%7)
				lecs = Lecture.objects.filter(lec_day__id = (date.weekday()+1)%7).filter(taken_by = user)
			# print(days_in_duration)
			# print(lecs)
				for lec in lecs:
					# print(Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time,lec_time__end_time__lte = lec.lec_time.end_time))
					faculty_list_for_adjusting_lec = User.objects.exclude(id__in = faculty_on_od).exclude(id__in = faculty_on_leave).exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_day = lec.lec_day,lec_time__start_time__gte = lec.lec_time.start_time,lec_time__end_time__lte = lec.lec_time.end_time)]).exclude(is_staff = True)
					# date_of_adjusting_lec = date
					adjust_opts[(lec,date)] = faculty_list_for_adjusting_lec 

			subject = 'Leave Request'
			# message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)
			message_data = {
				'leave' : new_leave[0],
				'duration' : duration,
			}
			# ---------------------------------TO FACULTY -------------------------------
			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			recipient_list.append(new_leave[0].leave_taken_by.email)
			html_content = render_to_string('email/faculty/leave_scheduled.html', message_data,request) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
							# print(l[0].for_lecture)
			send_async_mail(msg)
			# return render(request,'email/faculty/leave_scheduled.html', message_data)

			#---------------------------------TO HOD-------------------------------------
			authority = User.objects.filter(is_superuser = True)[0]
			message_data = {
				'leave' : new_leave[0],
				'duration' : duration,
				'authority' : authority,
			}
			recipient_list = []
			recipient_list.append(authority.email)
			html_content = render_to_string('email/hod/leave_request.html', message_data,request) # render with dynamic value
			text_content = strip_tags(html_content)
			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
			send_async_mail(msg)
			
			# return render(request,'email/hod/leave_request.html', message_data)


			context_data = {
				"adjust_opts" : adjust_opts,
				"leave" : new_leave[0]
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
def view_leaves(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if(request.method == 'POST'):
			leave = Leave.objects.get(pk = request.POST.get('leave_id'))
			if '_cancel' in request.POST:
				leave.delete()
		leaves = Leave.objects.filter(leave_taken_by = request.user)
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

		return render(request,"faculty/view_leaves.html",context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

@login_required
def submit_load_shift(request):
	if not request.user.is_superuser and not request.user.is_staff:
		user = User.objects.get(pk = request.user.id)
		if request.method == 'POST':
			# print(request.POST)
			if(request.POST.get('leave_id')):
				leave = Leave.objects.get(pk = request.POST.get('leave_id'))
				# print(leave)
				if('_apply' in request.POST):
					# print(request.POST.getlist('lecture_id'))
					if(request.POST.getlist('lecture_id')):
						for lec_id in request.POST.getlist('lecture_id'):
							lec = Lecture.objects.get(pk = lec_id)
							# print(lec)
							granted_to = list()
							for x in request.POST.getlist(str(lec.id)):
								granted_to.append(User.objects.get(pk = x))
							# print(request.POST.getlist('faculty_id'))
						# for faculty_id,lec_id in zip(request.POST.getlist('faculty_id'), request.POST.getlist('lecture_id')):
						# 	granted_to = faculty_id
							l = LoadShift.objects.get_or_create(leave = leave,for_lecture = lec)
							l[0].to_faculty.set(granted_to)
							# Email notificaion

							subject = 'New Load Shift request'
							# message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)

							email_from = settings.EMAIL_HOST_USER
							
							for faculty in granted_to:

								message_data = {
									'loadshift' : l[0],
									'granted_to' : faculty
								}
								recipient_list = []
								# print(faculty.id)
								recipient_list.append(faculty.email)
								html_content = render_to_string('email/faculty/loadshift_notification.html', message_data,request) # render with dynamic value
								text_content = strip_tags(html_content)

								msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
								msg.attach_alternative(html_content, "text/html")
								# print(l[0].for_lecture)
								send_async_mail(msg)
								
								# return render(request,'email/faculty/loadShift_notification.html', message_data)
						context_data = {
							"success" : True,
						}

					return render(request,"faculty/leave_request.html",context_data)
				
				elif('_cancel' in request.POST):
					
					leave.delete()

					return render(request,"faculty/leave_request.html",{})
								
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
	# print("HAHAHA")
	if not request.user.is_superuser and not request.user.is_staff:
		if(request.method == 'POST'):
			load_shift = LoadShift.objects.get(pk = request.POST.get('load_shift'))
			if '_reject' in request.POST:
				load_shift.to_faculty.remove(request.user)
			elif '_approve' in request.POST:
				load_shift.to_faculty.clear()
				load_shift.approved_status = True
				load_shift.to_faculty.set((request.user,))
				load_shift.save()

				subject = 'Loadshift accecpted'
				# message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)

				email_from = settings.EMAIL_HOST_USER
				

				message_data = {
					'loadshift' : load_shift,
					'accecpted_by' : request.user
				}
				recipient_list = []
				# print(faculty.id)
				if(load_shift.leave):
					recipient_list.append(load_shift.leave.leave_taken_by.email)
				else:
					recipient_list.append(load_shift.od.taken_by.email)
				html_content = render_to_string('email/faculty/loadshift_accept.html', message_data,request) # render with dynamic value
				text_content = strip_tags(html_content)

				msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
				msg.attach_alternative(html_content, "text/html")
				# print(l[0].for_lecture)
				send_async_mail(msg)

				# return render(request,'email/faculty/loadshift_accept.html', message_data)


		# user = User.objects.get(pk = request.user.id)
		load_shifts = LoadShift.objects.filter(to_faculty = request.user)
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


		context_data = {
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
						
					# ------------------- TO STUDENTS -------------------
				subject = "Makeup Lecture notificaion - " + makeup_lec.lec_subject.sname 

				message_data = {
					'makeup_lec' : makeup_lec,

				}
				email_from = settings.EMAIL_HOST_USER
				recipient_list = []
				# To be replaced by student email
				recipient_list.append("mandlekar.prashant.harshal@gmail.com")
				# print("###",recipient_list)
				html_content = render_to_string('email/student/makeup_notification.html', message_data,request) # render with dynamic value
				text_content = strip_tags(html_content)

				msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
				msg.attach_alternative(html_content, "text/html")
								# print(l[0].for_lecture)
				send_async_mail(msg)

				# return render(request,'email/student/makeup_notification.html', message_data)


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
			print("JHOLL af")
			return HttpResponseRedirect('./')

	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

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

				filtered_lecs = list(chain(lecs.filter(lec_time__start_time = timeslot.start_time),lecs.filter(lec_time__end_time = timeslot.end_time)))

				# lec_time__end_time__gte = timeslot.end_time)
				# print(timeslot,filtered_lecs)
				filtered_makeup_lecs = list(chain(makeup_lecs.filter(lec_time__start_time = timeslot.start_time),makeup_lecs.filter(lec_time__end_time = timeslot.end_time)))

				filtered_ia = ias.filter(ia_start_time__gte = timeslot.start_time,ia_end_time__lte = timeslot.end_time)

				filtered_guest_lecs = guest_lecs.filter(lec_time__start_time__lte = timeslot.end_time,lec_time__end_time__gte = timeslot.start_time)

				if(not filtered_lecs and not filtered_makeup_lecs and not filtered_ia.exists() and not filtered_guest_lecs.exists()):
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
def makeup_timeslots_api(request,syear,sdiv,sdate):
	# print(syear)
	# print(sdate)
	if not request.user.is_superuser and not request.user.is_staff:
		if(syear!='-1'):
			year = Year.objects.get(pk = int(syear))
			date = datetime.datetime.strptime(sdate,'%Y-%m-%d')
			day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
			div = Division.objects.get(pk = sdiv)
			lecs = Lecture.objects.filter(lec_day = day,lname__year = year,lec_div = div)
			# print(lecs)
			makeup_lecs = MakeupLecture.objects.filter(lec_date = date,year = year,division = div)
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

				filtered_lecs = list(chain(lecs.filter(lec_time__start_time = timeslot.start_time),lecs.filter(lec_time__end_time = timeslot.end_time)))

				# lec_time__end_time__gte = timeslot.end_time)
				# print(timeslot,filtered_lecs)
				filtered_makeup_lecs = list(chain(makeup_lecs.filter(lec_time__start_time = timeslot.start_time),makeup_lecs.filter(lec_time__end_time = timeslot.end_time)))

				filtered_ia = ias.filter(ia_start_time__gte = timeslot.start_time,ia_end_time__lte = timeslot.end_time)

				filtered_guest_lecs = guest_lecs.filter(lec_time__start_time__lte = timeslot.end_time,lec_time__end_time__gte = timeslot.start_time)

				if(not filtered_lecs and not filtered_makeup_lecs and not filtered_ia.exists() and not filtered_guest_lecs.exists()):
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
			lecs = Lecture.objects.filter(lec_time__start_time = timeslot.start_time,lec_day = day) | Lecture.objects.filter(lec_time__end_time = timeslot.end_time,lec_day = day)
			makeup_lecs = MakeupLecture.objects.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time,lec_date = date)
			ias = IA.objects.filter(ia_date = date, ia_start_time__lte = timeslot.end_time,ia_end_time__gte = timeslot.start_time)
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
			# timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
			# room = Room.objects.get(pk = int(request.POST.get('locations')))
			start_time = datetime.datetime.strptime(request.POST.get('start_time'),'%H:%M').time()
			end_time = datetime.datetime.strptime(request.POST.get('end_time'),'%H:%M').time()


			try:
				ia = IA.objects.get_or_create(ia_year = year, ia_subject = subject,ia_date = date,ia_start_time = start_time,ia_end_time = end_time)

				batches = Batch.objects.filter(batch_of_year = year)
				rooms = Room.objects.all()
				supervisors = User.objects.filter(is_superuser = False)
				context_data = {
					"ia" : ia[0],
					"rooms" : rooms,
					"batches" : batches,
					"supervisors" : supervisors,
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
def post_ia_arrangement(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if request.method == 'POST':
			ia = IA.objects.get(pk = request.POST.get('ia_id'))
			# batch_room_dict = dict()			
			for batch in Batch.objects.filter(batch_of_year = ia.ia_year):
				batch_room_id = request.POST.get(str(batch)+"-room")
				batch_supervisor_id = request.POST.get(str(batch)+"-supervisor")
				# print("###",batch_supervisor_id)
				if(batch_room_id != "-1" and batch_supervisor_id != "-1" and batch_room_id !="" and batch_supervisor_id != ""):
					batch_room = Room.objects.get(pk = batch_room_id)
					batch_supervisor = User.objects.get(pk = batch_supervisor_id)
					# print("###",batch_supervisor)
					# batch_room_dict[batch] = (batch_room,batch_supervisor)
					try:
						mapping = IaBatchRoomMapping(ia= ia,batch = batch,room=batch_room,supervisor= batch_supervisor)
						# mapping.full_clean()
						# mapping.save()



					except Exception as e:
						context_data = {
							"errors" : e
						}

			# ------------------- TO STUDENTS -------------------
			subject = "IA notificaion - " + ia.ia_subject.sname 

			ia_mappings = IaBatchRoomMapping.objects.filter(ia = ia)

			message_data = {
				'ia' : ia,
				'ia_mappings' : ia_mappings,

			}
			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			# To be replaced by student email
			recipient_list.append("mandlekar.prashant.harshal@gmail.com")
			# print("###",recipient_list)
			html_content = render_to_string('email/student/ia_notification.html', message_data,request) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
							# print(l[0].for_lecture)
			send_async_mail(msg)

			# return render(request,'email/student/ia_notification.html', message_data)				
			# -------------------TO ALLOCATED SUPERVISOR FACULTY AND ASSISTANTS--------------
			subject = "IA notificaion - " + ia.ia_subject.sname 

			ia_mappings = IaBatchRoomMapping.objects.filter(ia = ia)

			message_data = {
				'ia' : ia,
				'ia_mappings' : ia_mappings,

			}
			email_from = settings.EMAIL_HOST_USER
			recipient_list = []

			for ia_mapping in ia_mappings:
				recipient_list.append(ia_mapping.supervisor.email)
			# print("###",recipient_list)
			html_content = render_to_string('email/faculty/ia_notification.html', message_data,request) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
							# print(l[0].for_lecture)
			send_async_mail(msg)

			# return render(request,'email/faculty/ia_notification.html', message_data)	

			context_data = {
				"success" : True,
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
		timeslots = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff__lte= datetime.timedelta(hours = 2))

		context_data = {
			"years" : years,
			"subjects" : subjects,
			"timeslots" : timeslots

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
			title = None
			subject = None
			year = Year.objects.get(pk = int(request.POST.get('year')))
			if(request.POST.get('subject') == '0'):
				title = request.POST.get('title')
			else:
				subject = Subject.objects.get(pk = int(request.POST.get('subject')))
			date = datetime.datetime.strptime(request.POST.get('guestlec_date'),'%m/%d/%Y')
			timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
			room = Room.objects.get(pk = int(request.POST.get('locations')))
			day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
			lecs_in_timeslot = Lecture.objects.filter(lec_time__start_time = timeslot.start_time,lec_day = day,lname__year = year) | Lecture.objects.filter(lec_time__end_time = timeslot.end_time,lec_day = day,lname__year = year)

			
			try:
				if(subject):
					guest_lecture = GuestLecture(lec_year = year, lec_subject = subject,lec_date = date,lec_time = timeslot,lec_in = room)
				else:
					guest_lecture = GuestLecture(lec_year = year, title = title,lec_date = date,lec_time = timeslot,lec_in = room)
				guest_lecture.full_clean()
				# # print(guest_lecture)
				guest_lecture.save()

				subject = 'Expert Lecture'
				# message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)
				# --------------------------------TO FACULTY WITH CONFLICTING TIMESLOTS---------
				for _ in lecs_in_timeslot:
					message_data = {
						'guest_lecture' : guest_lecture,
						'faculty' : _.taken_by,
						'conflicting_lecture' : _, 

					}
					email_from = settings.EMAIL_HOST_USER
					recipient_list = []
					recipient_list.append(_.taken_by.email)
					print("###",recipient_list)
					html_content = render_to_string('email/faculty/expert_lecture_conflicting_notification.html', message_data,request) # render with dynamic value
					text_content = strip_tags(html_content)

					msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
					msg.attach_alternative(html_content, "text/html")
									# print(l[0].for_lecture)
					send_async_mail(msg)

					# return render(request,'email/faculty/expert_lecture_conflicting_notification.html', message_data)				

				# ---------------------------------TO ALL FACULTY -------------------------------
				email_from = settings.EMAIL_HOST_USER
				recipient_list = []

				staff_list = User.objects.filter(is_staff = False,is_superuser = False).exclude(pk__in=[x.id  for x in lecs_in_timeslot])
				for _ in staff_list:
					recipient_list.append(_.email)
				html_content = render_to_string('email/faculty/expert_lecture_notification.html', message_data,request) # render with dynamic value
				text_content = strip_tags(html_content)

				msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
				msg.attach_alternative(html_content, "text/html")
								# print(l[0].for_lecture)
				send_async_mail(msg)

				# return render(request,'email/faculty/expert_lecture_notification.html', message_data)

				#---------------------------------TO HOD-------------------------------------
				authority = User.objects.filter(is_superuser = True)[0]
				message_data = {
					'lecture' : guest_lecture,
					'authority' : authority,
				}
				recipient_list = []
				recipient_list.append(authority.email)
				html_content = render_to_string('email/hod/expert_lecture_notification.html', message_data,request) # render with dynamic value
				text_content = strip_tags(html_content)
				msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
				msg.attach_alternative(html_content, "text/html")
				send_async_mail(msg)

				# return render(request,'email/hod/expert_lecture_notification.html', message_data)

				context_data = {
					"success" : 'true'
				}

				# return render(request,"faculty/guestlecture.html",context_data)

			except Exception as e:
				# print(e)
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
			taken_by = request.user

			scope = request.POST.get('scope')

			new_od = OD.objects.get_or_create(od_type = od_type, od_title = title, od_details = og_details, supporting_organisation = supporting_og, from_date = from_date, to_date = to_date, last_date = last_date, fees = fees,scope = scope, taken_by = taken_by)
			try:
				correspondence_filename = request.FILES[u'correspondence'].name
				correspondence_file = request.FILES['correspondence']
				new_od[0].correspondence.save(correspondence_filename,correspondence_file)
				new_od[0].save()
			except Exception as e:
				# print(e)
				pass
			# days_in_duration = list()
			adjust_opts = dict()
			faculty_on_leave = [x.leave_taken_by.id for x in Leave.objects.filter(leave_start_date__lte = to_date,leave_end_date__gte = from_date).exclude(approved_status = True).exclude(approved_status = None)]
			faculty_on_od = [x.taken_by.id for x in OD.objects.filter(from_date__lte = to_date,to_date__gte = from_date).exclude(approved_status = True).exclude(approved_status = None)]
			# print("$$",faculty_on_leave)
			# print("##",faculty_on_od)
			for date in daterange(from_date,to_date+datetime.timedelta(days=1)):
				# print(date,(date.weekday()+1)%7)
				# days_in_duration.append((date.weekday()+1)%7)
				lecs = Lecture.objects.filter(lec_day__id = (date.weekday()+1)%7).filter(taken_by = taken_by)
			# print(days_in_duration)
			# print(lecs)
				for lec in lecs:
					# print(Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time,lec_time__end_time__lte = lec.lec_time.end_time))
					faculty_list_for_adjusting_lec = User.objects.exclude(id__in = faculty_on_od).exclude(id__in = faculty_on_leave).exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_day = lec.lec_day,lec_time__start_time__gte = lec.lec_time.start_time,lec_time__end_time__lte = lec.lec_time.end_time)]).exclude(is_staff = True)
					# date_of_adjusting_lec = date
					adjust_opts[(lec,date)] = faculty_list_for_adjusting_lec 

			# print(adjust_opts)
			subject = 'OD Request'
			# message = 'Lecture : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(leave.leave_taken_by.username)
			message_data = {
				'od' : new_od[0],
			}
			# ---------------------------------TO FACULTY -------------------------------
			email_from = settings.EMAIL_HOST_USER
			recipient_list = []
			recipient_list.append(new_od[0].taken_by.email)
			html_content = render_to_string('email/faculty/leave_scheduled.html', message_data,request) # render with dynamic value
			text_content = strip_tags(html_content)

			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
							# print(l[0].for_lecture)
			send_async_mail(msg)

			# return render(request,'email/faculty/od_scheduled.html', message_data)

			#---------------------------------TO HOD-------------------------------------
			authority = User.objects.filter(is_superuser = True)[0]
			message_data = {
				'od' : new_od[0],
				'authority' : authority,
			}
			recipient_list = []
			recipient_list.append(authority.email)
			html_content = render_to_string('email/hod/leave_request.html', message_data,request) # render with dynamic value
			text_content = strip_tags(html_content)
			msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
			msg.attach_alternative(html_content, "text/html")
			send_async_mail(msg)

			# return render(request,'email/hod/od_request.html', message_data)

			context_data = {
				"adjust_opts" : adjust_opts,
				"od" : new_od[0]
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
				if('_apply' in request.POST):
					if(request.POST.getlist('lecture_id')):
						for lec_id in request.POST.getlist('lecture_id'):
							# print("$$$",lec_id)
							lec = Lecture.objects.get(pk = int(lec_id))
							# print(lec)
							granted_to = list()
							for x in request.POST.getlist(str(lec.id)):
								granted_to.append(User.objects.get(pk = x))
						# print(request.POST.getlist('faculty_id'))
						# for faculty_id,lec_id in zip(request.POST.getlist('faculty_id'), request.POST.getlist('lecture_id')):
						# 	granted_to = faculty_id
							l = LoadShift.objects.get_or_create(od = od,for_lecture = lec)
							l[0].to_faculty.set(granted_to)
							# Email notificaion

							subject = 'New Load Shift request'
							message = 'OD : ' + str(Lecture.objects.get(pk = lec_id).lname.sname) +'/n From : ' + str(od.taken_by.username)

							message_data = {
								'loadshift' : l[0],
							}

							email_from = settings.EMAIL_HOST_USER
							recipient_list = []
							for faculty in granted_to:
								# print(faculty_id)
								recipient_list.append(faculty.email)
							html_content = render_to_string('email/loadshift_notification.html', message_data,request) # render with dynamic value
							text_content = strip_tags(html_content)

							msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
							msg.attach_alternative(html_content, "text/html")
							# print(l[0].for_lecture)
							send_async_mail(msg)


						context_data = {
							"success" : 'true',
						}
				elif('_cancel' in request.POST):
					od.delete()
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
		# print(email_from)
		recipient_list = ['harshal.pm@somaiya.edu',]
		html_content = render_to_string('email/approve_notification.html', {'varname':'value'}) # render with dynamic value
		text_content = strip_tags(html_content)

		msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
		msg.attach_alternative(html_content, "text/html")

		# send_async_mail(msg)

		# send_async_mail(msg)
		return render(request,'email/hod/leave_request.html',{})
		return HttpResponse("Success")
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)



@login_required
def api_home(request):
	
	return render(request,"faculty/api_home.html")

	# html_error_data = {
	# 	"error_code" : "401",
	# 	"error_message" : "UNAUTHORIZED"
	# }
	# return render(request,"error.html",html_error_data)

@login_required
def api_free_rooms(request):
	if not request.user.is_superuser and not request.user.is_staff:
		if request.method == 'POST':
			# print("AJAX CALLED")
			# print(request.POST.get('date'))
			date = datetime.datetime.strptime(request.POST.get('date'),'%m/%d/%Y')
			timeslot = TimeSlot.objects.get(pk = request.POST.get('timeslot_id'))
			day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
			lecs = Lecture.objects.filter(lec_time__start_time = timeslot.start_time,lec_day = day) | Lecture.objects.filter(lec_time__end_time = timeslot.end_time,lec_day = day)
			makeup_lecs = MakeupLecture.objects.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time,lec_date = date)
			ias = IA.objects.filter(ia_date = date, ia_start_time__lte = timeslot.end_time,ia_end_time__gte = timeslot.start_time)
			guest_lecs = GuestLecture.objects.filter(lec_date = date, lec_time__start_time__gte = timeslot.start_time,lec_time__end_time__lte = timeslot.end_time)
			occupied_rooms = list()
			for lec in lecs:
				occupied_rooms.append(lec.lec_in)
			for lec in makeup_lecs:
				occupied_rooms.append(lec.lec_in)
			for ia in ias:
				ia_mappings = IaBatchRoomMapping.objects.filter(ia=ia)
				for ia_mapping in ia_mappings:
					occupied_rooms.append(ia_mapping.room)
			for lec in guest_lecs:
				occupied_rooms.append(lec.lec_in)

			rooms = Room.objects.exclude(room__in = occupied_rooms)
			rooms_json = serializers.serialize("json",rooms)
			return HttpResponse(rooms_json)
		
		timeslots = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff__lte= datetime.timedelta(hours = 2))

		context_data = {
			"timeslots" : timeslots,
		}
		return render(request,"faculty/api_free_rooms.html",context_data)
	html_error_data = {
		"error_code " : "401",
		"error_message" : "UNAUTHORIZED"
 
	}

@login_required
def api_available(request):
	if request.method == 'POST':
		date = datetime.datetime.strptime(request.POST.get('date'),'%m/%d/%Y')
		
		faculty_on_leave = [x.leave_taken_by.id for x in Leave.objects.filter(leave_start_date__lte = date,leave_end_date__gte = date,approved_status = True)]
		faculty_on_od = [x.taken_by.id for x in OD.objects.filter(from_date__lte = date,to_date__gte = date,approved_status = True)]
		
		available_faculty = User.objects.exclude(pk__in = (faculty_on_leave+faculty_on_od))



		available_faculty_json = serializers.serialize("json",available_faculty)

		return HttpResponse(available_faculty_json)

	faculty_on_leave = [x.leave_taken_by.id for x in Leave.objects.filter(leave_start_date__lte = datetime.datetime.now(),leave_end_date__gte = datetime.datetime.now()).exclude(approved_status = False)]
	faculty_on_od = [x.taken_by.id for x in OD.objects.filter(from_date__lte = datetime.datetime.now(),to_date__gte = datetime.datetime.now()).exclude(approved_status = False)]
	
	available_faculty = User.objects.exclude(pk__in = (faculty_on_leave+faculty_on_od))

	context_data = {
		"available_faculty" : available_faculty,
	}
	# print()
	return render(request,"faculty/api_available_faculty.html",context_data)


