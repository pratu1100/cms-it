from django.shortcuts import render
from faculty.models import TimeSlot,Lecture,Subject,Year,Division,DaysOfWeek,Batch,Room
from django.db.models import DurationField, F, ExpressionWrapper
from django.contrib.auth.models import User

import datetime
# # Create your views here.
# <QueryDict: 
# {'csrfmiddlewaretoken': ['L25PIXgWSCAXzTMTmjJVsPcHA1gDkwUIzsrSNODtW8fZutyhHTO14mYZ5ToCMnkd'],
#  'termopt': ['odd'],
#   'yearopt': ['SY'], 
#   'divopt': ['A'],
#   'dayopt': ['monday'],
#   '10:30 - 11:30': ['M4'], 
#   '10:30 - 12:30': ['COA'], 
#   '11:30 - 12:30': ['0'], 
#   '13:15 - 14:15': ['0'], 
#   '14:15 - 15:15': ['0'], 
#   '13:15 - 15:15': ['DCN'], 
#   '15:15 - 16:15': ['0'], 
#   '16:15 - 17:15': ['0'], 
#   '15:15 - 17:15': ['WP'], 
#   'finish': ['Finish']
#  }

# dict = {
#     'csrfmiddlewaretoken': ['A3V0O22VfP80ZY3xmVVq6xbdV0Lwbov8oth3TTpsjlN2UyPVHv0wI4XvqSTvDfVD '], '
#         'termopt ': ['odd '],
#         'yearopt ': ['SY '],
#         'divopt ': ['A '], 
#         'dayopt': ['Monday'], 
#         '10:30 - 11:30': ['0'], 
#         '10:30 - 11:30-A1': ['1'], 
#         '10:30 - 11: 30 - A2 ': [' 1 '], 
#         '10: 30 - 11: 30 - A3 ': [' 1 '], 
#         '10: 30 - 11: 30 - A4 ': [' 1 '], 
#         '10:30 - 12: 30 ': ['DCN - 4 '], 
#         '10: 30 - 12: 30 - A1 ': [' 1 '], 
#         '10: 30 - 12: 30 - A2 ': [' 1 '], 
#         '10: 30 - 12: 30 - A3 ': [' 1 '], 
#         '10: 30 - 12: 30 - A4 ': [' 1 '], 
#         '11: 30 - 12: 30 ': [' 0 '], 
#         '11:30 - 12: 30 - A1 ': [' 1 '], 
#         '11: 30 - 12: 30 - A2 ': [' 1 '], 
#         '11: 30 - 12: 30 - A3 ': [' 1 '], 
#         '11: 30 - 12: 30 - A4 ': [' 1 '], 
#         '13: 15 - 14: 15 ': [' 0 '], 
#         '13: 15 - 14: 15 - A1 ': [' 1 '], 
#         '13: 15 - 14: 15 - A2 ': [' 1 '], 
#         '13: 15 - 14: 15 - A3 ': [' 1 '], 
#         '13: 15 - 14: 15 - A4 ': [' 1 '], 
#         '14:15 - 15: 15 ': [' 0 '], 
#         '14: 15 - 15: 15 - A1 ': [' 1 '], 
#         '14: 15 - 15: 15 - A2 ': [' 1 '], 
#         '14: 15 - 15: 15 - A3 ': [' 1 '], 
#         '14: 15 - 15: 15 - A4 ': [' 1 '], 
#         '13: 15 - 15: 15 ': [' 0 '], 
#         '13: 15 - 15: 15 - A1 ': [' 1 '], 
#         '13: 15 - 15: 15 - A2 ': [' 1 '], 
#         '13: 15 - 15: 15 - A3 ': [' 1 '], 
#         '13: 15 - 15: 15 - A4 ': [' 1 '], 
#         '15: 15 - 16: 15 ': [' 0 '], 
#         '15: 15 - 16: 15 - A1 ': [' 1 '], 
#         '15: 15 - 16: 15 - A2 ': [' 1 '], 
#         '15: 15 - 16: 15 - A3 ': [' 1 '], 
#         '15: 15 - 16: 15 - A4 ': [' 1 '], 
#         '16: 15 - 17: 15 ': [' 0 '], 
#         '16: 15 - 17: 15 - A1 ': [' 1 '], 
#         '16: 15 - 17: 15 - A2 ': [' 1 '], 
#         '16: 15 - 17: 15 - A3 ': [' 1 '], 
#         '16: 15 - 17: 15 - A4 ': [' 1 '], 
#         '15: 15 - 17: 15 ': [' 0 '], 
#         '15: 15 - 17: 15 - A1 ': [' 1 '], 
#         '15: 15 - 17: 15 - A2 ': [' 1 '], 
#         '15: 15 - 17: 15 - A3 ': [' 1 '], 
#         '15: 15 - 17: 15 - A4 ': [' 1 '], 
#         'finish ': [' Finish ']
#         }

def get_timetable(request):
	errors = None
	if(request.method == 'POST'):
		t_year = Year.objects.filter(year = request.POST.get('yearopt'))[0]
		t_div = Division.objects.filter(division = request.POST.get('divopt'))[0]
		t_day = DaysOfWeek.objects.filter(day_name = request.POST.get('dayopt'))[0]
		print(request.POST)
		ts = TimeSlot.objects.all();
		for t in ts:
			tavail = request.POST.get(str(t))
			if(tavail!='0' and tavail!=None):
				print(t)
				print("###")
				print(tavail)
				print(tavail.split("-")[0])
				print(tavail.split("-")[1])
				u = User.objects.get(pk= int(tavail.split("-")[1]))
				s = Subject.objects.filter(sname = tavail.split("-")[0])[0]
				l = Lecture(lname = s, taken_by = u, lec_day = t_day, lec_time = t, lec_div = t_div)
				# print(l.taken_by)
				try:
					l.save()
				except Exception as e:
					print("Already exist at same time")
					errors = 'Conflicting timeslot ' + str(t) 


	time_slots = TimeSlot.objects.annotate(
    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
	).filter(diff__lte=datetime.timedelta(hours = 2))
	
	subjects = Subject.objects.all();

	batches = Batch.objects.all();

	rooms = Room.objects.all();

	context_data = {
		"errors" : errors,
		"timeslots" : time_slots,
		"subjects" : subjects,
		"batches" : batches,
		"rooms" : rooms
	}
	return render(request,'assistant/updatett.html',context_data)