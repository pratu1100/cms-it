from django.shortcuts import render, HttpResponseRedirect,HttpResponse
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift,MakeupLecture,Year, Division, Room,IA
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import DurationField, F, ExpressionWrapper
import time
import json
from django.core import serializers
# # Update leave as approved by HOD
# def update_leave(request, leave_id):  
#     Leave.objects.filter(id=leave_id).update(is_approved=True)
#     return HttpResponseRedirect('/hod/')

@login_required
def create_leave(request):
	return render(request,"faculty/leave_request.html",{})

@login_required
def submit_leave(request):
	if request.method == 'POST':
		user = User.objects.get(pk = request.user.id)
		start_date_val = request.POST.get('leave_start_date')
		end_date_val = request.POST.get('leave_end_date')	
		start_time_val = request.POST.get('leave_start_time')
		end_time_val = request.POST.get('leave_end_time')
		start_date_time = start_date_val + 'T' + start_time_val
		end_date_time = end_date_val + 'T' + end_time_val
		# Python date time objects
		start_date = datetime.datetime.strptime(start_date_time, '%d/%m/%YT%H:%M')
		end_date = datetime.datetime.strptime(end_date_time, '%d/%m/%YT%H:%M')
		lecs = Lecture.objects.filter(lec_day__id__in = range(start_date.weekday(),end_date.weekday()+1)).filter(taken_by = user).filter(lec_time__start_time__gte = datetime.time(start_date)).filter(lec_time__end_time__lte = datetime.time(end_date))
		adjust_opts = dict()
		new_leave = Leave.objects.get_or_create(leave_taken_by = user,leave_start_date=start_date.date(),leave_end_date = end_date.date(),leave_start_time=start_date.time(),leave_end_time = end_date.time())
		print("####",new_leave)
		for lec in lecs:
			adjust_opts[lec] = User.objects.exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time)])
		print(adjust_opts)
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

@login_required
def submit_load_shift(request):
	user = User.objects.get(pk = request.user.id)
	load_shifts = LoadShift.objects.filter(to_faculty = user)
	if request.method == 'POST':
		print(request.POST)
		if(request.POST.get('leave_id')):
			leave = Leave.objects.get(pk = request.POST.get('leave_id'))
			print(leave)
			print(request.POST.getlist('lecture_id'))
			if(request.POST.getlist('lecture_id')):
				for faculty_id,lec_id in zip(request.POST.getlist('faculty_id'), request.POST.getlist('lecture_id')):
					LoadShift.objects.get_or_create(leave = leave,to_faculty = User.objects.get(pk = faculty_id),for_lecture = Lecture.objects.get(pk = lec_id))
		else:
			print("No load shifts")
		# print(user.username)
		# print(for_lec)
		# print(to_faculty)
	return render(request,"faculty/loadshift.html",{"load_shifts":load_shifts})

@login_required
def get_makeup(request):
	days = DaysOfWeek.objects.all().exclude(day_name__in = ('Sunday','Saturday'))
	m_lecs = MakeupLecture.objects.filter(lec_date__lte = datetime.datetime.now()+datetime.timedelta(days = 7))
	print("$#$#$#",m_lecs)
	years = Year.objects.all()
	divions = Division.objects.all()
	subjects = Subject.objects.all()
	timeslots = TimeSlot.objects.annotate(
    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
	).filter(diff__lte= datetime.timedelta(hours = 1))


	free = dict()

	for day in days:
		print(day.id)
		# m_lecs = MakeupLecture.objects.filter(lec_date__week_day = day.id)
		free_ts = list()
		for timeslot in timeslots:
			try:
				print("******",MakeupLecture.objects.filter(lec_date__week_day = (day.id +1) , lec_time = timeslot)[0].lec_date.strftime("%A"))
			
			except:
				pass
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

def post_makeup(request):
	success = False
	if(request.method == "POST"):
		print(request.POST)
		year = Year.objects.get(pk = int(request.POST.get('year')))
		subject = Subject.objects.get(pk = int(request.POST.get('subject')))
		division = Division.objects.get(pk = int(request.POST.get('division')))
		date = datetime.datetime.strptime(request.POST.get('makeup_date'),'%m/%d/%Y')
		timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
		user = User.objects.get(pk = request.user.id)
		print(year,"--",subject,"--",division,"--",date,"--",timeslot)
		makeup_lec = MakeupLecture(year = year, lec_subject = subject, division = division,lec_date = date, lec_time = timeslot, lec_taken_by = user)
		try:
			makeup_lec.full_clean()
			makeup_lec.save()
			success = True
			context_data = {
				"success" : success ,
			}
		except Exception as e:
			print("Cannnot save",e)
			success = False
			context_data = {
				"errors" : success ,
			}

		return render(request,"faculty/makeup.html",context_data)
	else:
		return HttpResponseRedirect('./')


# def get_subjects(request,yid):
# 	print("request")
# 	try:
# 		year = Year.objects.get(pk = yid)
# 		subjects = Subject.objects.filter(year = year)
# 		print(subjects)
# 	except:
		

# 	return HttpResponse("<h1>Test</h1>")

def get_timeslots(request,syear,sdate):
	print(syear)
	print(sdate)

	if(syear!='-1'):
		year = Year.objects.get(pk = int(syear))
		date = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
		lecs = Lecture.objects.filter(lec_day = day,lname__year = year)
		# print(lecs)
		makeup_lecs = MakeupLecture.objects.filter(lec_date = date,year = year)
		# print(makeup_lecs)
		ias = IA.objects.filter(ia_date = date, ia_year =year)
		timeslots = TimeSlot.objects.annotate(
    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
	).filter(diff__lte= datetime.timedelta(hours = 2))
		# print(timeslots)
		# occupied_rooms = list()
		free_ts = list()
		for timeslot in timeslots:
			# print(timeslot)
			filtered_lecs = lecs.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time)
			# print(filtered_lecs)
			# for lec in filtered_lecs:
			# 	occupied_rooms.append(lec.lec_in)

			filtered_makeup_lecs = makeup_lecs.filter(lec_time__start_time__gte = timeslot.start_time,lec_time__end_time__lte = timeslot.end_time)
			# print(filtered_makeup_lecs.exists())
			# for lec in filtered_makeup_lecs:
			# 	occupied_rooms.append(lec.lec_in)
			filtered_ia = ias.filter(ia_time__start_time__gte = timeslot.start_time,ia_time__end_time__lte = timeslot.end_time)
			if(not filtered_lecs.exists() and not filtered_makeup_lecs.exists() and not filtered_ia.exists()):
				free_ts.append(timeslot)
		# print(lecs)
		# print(makeup_lecs)
		ts_json = serializers.serialize("json",free_ts)
		
		# rooms_json = serializers.serialize("json",occupied_rooms)

		# data_json = {
		# 	"timeslots" : ts_json,
		# 	"rooms" : rooms_json
		# }
		print(ts_json)
		return HttpResponse(ts_json)
	else:
		return HttpResponse("Select Year")

def get_available_rooms(request,sdate,slot):
	print(sdate)
	print(slot)
	if(slot!='-1'):
		date = datetime.datetime.strptime(sdate,'%Y-%m-%d')
		day = DaysOfWeek.objects.get(day_name = date.strftime('%A'))
		timeslot = TimeSlot.objects.get(pk = int(slot))
		lecs = Lecture.objects.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time,lec_day = day)
		makeup_lecs = MakeupLecture.objects.filter(lec_time__start_time__gte = timeslot.start_time, lec_time__end_time__lte = timeslot.end_time,lec_date = date)
		ias = IA.objects.filter(ia_date = date, ia_time__start_time__gte = timeslot.start_time,ia_time__end_time__lte = timeslot.end_time)
		occupied_rooms = list()
		for lec in lecs:
			occupied_rooms.append(lec.lec_in)
		for lec in makeup_lecs:
			occupied_rooms.append(lec.lec_in)
		for ia in ias:
			occupied_rooms.append(ia.ia_in)

		rooms = Room.objects.exclude(room__in = occupied_rooms)
		rooms_json = serializers.serialize("json",rooms)
		return HttpResponse(rooms_json)
	else:
		return HttpResponse("Select TimeSlot")



def get_ia(request):
	years = Year.objects.all()
	subjects = Subject.objects.all()

	context_data = {
		"years" : years,
		"subjects" : subjects
	}

	return render(request,"faculty/ia.html",context_data)

def post_ia(request):
	if(request.method == 'POST'):
		print(request.POST)
		year = Year.objects.get(pk = int(request.POST.get('year')))
		subject = Subject.objects.get(pk = int(request.POST.get('subject')))
		date = datetime.datetime.strptime(request.POST.get('ia_date'),'%m/%d/%Y')
		timeslot = TimeSlot.objects.get(pk = int(request.POST.get('timeslot')))
		room = Room.objects.get(pk = int(request.POST.get('locations')))

		try:
			ia = IA(ia_year = year, ia_subject = subject,ia_date = date,ia_time = timeslot,ia_in = room)
			ia.full_clean()
			print(ia)
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
