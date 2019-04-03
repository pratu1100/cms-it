from django.shortcuts import render, HttpResponseRedirect
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
import time
# # Update leave as approved by HOD
# def update_leave(request, leave_id):  
#     Leave.objects.filter(id=leave_id).update(is_approved=True)
#     return HttpResponseRedirect('/hod/')

@login_required
def create_leave(request):
	uname = User.objects.get(pk = request.user.id)
	if request.method == 'POST':
		date_val = request.POST.get('leave_date')

		start_time_val = request.POST.get('leave_start_time')
		end_time_val = request.POST.get('leave_end_time')
		
		# print(request.POST)
		date_time = date_val + 'T' + start_time_val
		day_name = datetime.strptime(date_time, '%b %d, %YT%H:%M %p')
		end_timing = 
		time = TimeSlot(start_time = datetime.time(day_name),end_time = datetime.time(da))
		Leave.objects.create(leave_taken_by=uname,leave_time = datetime.time(day_name),leave_date = datetime.date(day_name))
		lecs = Lecture.objects.filter(lec_day__day_name = day_name.strftime("%A")).filter(taken_by = uname).filter(lec_time__start_time__gte = datetime.time(day_name))
		adjust_opts = dict()
		for lec in lecs:
			# adjust_opts[lec.lname.sname] = [x for x in User.objects.all() if len(Lecture.objects.filter(lec_day__day_name = day_name.strftime("%A")).filter(taken_by = x).filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time))>0] 
			adjust_opts[lec.lname.sname] = User.objects.exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time)])
		print(adjust_opts)
		return render(request,"faculty/leave_request.html",{"lecs": lecs,"adjust_opts":adjust_opts})
	return render(request,"faculty/leave_request.html",{})

@login_required
def submit_leave(request,id):
	if(request.method == "POST"):
		user = User.objects.get(pk=request.user.id)
		Leave.objects.create(leave_taken_by = user,)
		LoadShift.objects.create()
