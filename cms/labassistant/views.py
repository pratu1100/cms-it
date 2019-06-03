from django.shortcuts import render
from faculty.models import TimeSlot,Lecture,Subject
from django.db.models import DurationField, F, ExpressionWrapper
import datetime
# Create your views here.
def get_timetable(request):
	if(request.method == 'POST'):
		print(request.POST)

	time_slots = TimeSlot.objects.annotate(
    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
	).filter(diff__lte=datetime.timedelta(hours = 2))
	
	subjects = Subject.objects.all();

	context_data = {
		"timeslots" : time_slots,
		"subjects" : subjects
	}
	return render(request,'assistant/updatett.html',context_data)