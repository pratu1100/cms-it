from django.shortcuts import render, HttpResponseRedirect
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject
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
		date_time = request.POST.get('leave_data')
		day_name = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')
		print(type(day_name))
		lecs = Lecture.objects.filter(lec_day__day_name = day_name.strftime("%A")).filter(taken_by = uname).filter(lec_time__start_time__gte = datetime.time(day_name))
		adjust_opts = dict()
		for lec in lecs:
			# adjust_opts[lec.lname.sname] = [x for x in User.objects.all() if len(Lecture.objects.filter(lec_day__day_name = day_name.strftime("%A")).filter(taken_by = x).filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time))>0] 
			adjust_opts[lec.lname.sname] = User.objects.exclude(id__in = [x.taken_by.id for x in Lecture.objects.filter(lec_time__start_time__gte = lec.lec_time.start_time).filter(lec_time__end_time__lte = lec.lec_time.end_time)])
		print(adjust_opts)
		return render(request,"faculty/leave_request.html",{"lecs": lecs,"adjust_opts":adjust_opts})
	return render(request,"faculty/leave_request.html",{})