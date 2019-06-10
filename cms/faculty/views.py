from django.shortcuts import render, HttpResponseRedirect,HttpResponse
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from django.db.models import DurationField, F, ExpressionWrapper
import time
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
	timeslots = TimeSlot.objects.annotate(
    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
	).filter(diff__lte= datetime.timedelta(hours = 1))


	free = dict()

	for day in days:
		# print(day)
		free_ts = list()
		for timeslot in timeslots:
			if(not Lecture.objects.filter(lec_day = day,lec_time = timeslot).exists()):
				free_ts.append(timeslot)
		free[day] = free_ts
	print(free)

	context_data = {
		"free_slots" : free,
	}

	return render(request,"faculty/makeup.html",context_data)

