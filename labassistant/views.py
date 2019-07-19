from django.shortcuts import render,HttpResponse
from faculty.models import TimeSlot,Lecture,Subject,Year,Division,DaysOfWeek,Batch,Room
from django.db.models import DurationField, F, ExpressionWrapper
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
from django.core import serializers
from django.http import JsonResponse

import datetime

@login_required
def get_timetable(request):
	if request.user.is_staff:
		errors = None
		if(request.method == 'POST'):
			t_year = Year.objects.filter(year = request.POST.get('yearopt'))[0]
			t_div = Division.objects.filter(division = request.POST.get('divopt'))[0]
			t_day = DaysOfWeek.objects.filter(day_name = request.POST.get('dayopt'))[0]
			# print(request.POST)
			# For lectures
			ts = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff__lt=datetime.timedelta(hours = 2))
			
			for t in ts:
				# print(t)
				tavail = request.POST.getlist(str(t))
				# print(tavail[0])
				# print(tavail[1])
				if(tavail[0]!='0' and tavail[1]!=None):
					# print(t)
					# print("###")
					# print(tavail)
					# print(tavail.split("-")[0])
					# print(tavail.split("-")[1])

					u = User.objects.get(pk= int(tavail[0].split("-")[1]))
					s = Subject.objects.get(pk = tavail[0].split("-")[0])
					r = Room.objects.get(pk = tavail[1])
					# print(u)
					# print(s)
					# print(r)

					try:
						l = Lecture.objects.get(lec_day = t_day,lec_time = t,lec_div = t_div) 
						# print(l)
						if not (l.taken_by == u):
							l.taken_by = u
						if not (l.lname == s):
							l.lname = s
						if not (l.lec_in == r):
							l.lec_in = r
						l.save()
					except:
						# print("Creating new lecture..")
						l = Lecture(lname = s, lec_day = t_day, lec_time = t, lec_div = t_div, taken_by = u, lec_in = r)
						l.full_clean()
						l.save()

			ts = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff=datetime.timedelta(hours = 2))

			for t in ts: 
				# print(t)
				for batch in Batch.objects.filter(batch_of_year = t_year,batch_of_div = t_div):
					tavail = request.POST.getlist(str(t)+"-"+str(batch.batch))
					
					if(tavail[0]!='0' and tavail[1]!=None):

						# print(tavail)


						u = User.objects.get(pk= int(tavail[0].split("-")[1]))
						s = Subject.objects.get(pk = tavail[0].split("-")[0])
						r = Room.objects.get(pk = tavail[1])

						try:
							l = Lecture.objects.get(lec_day = t_day,lec_time = t,lec_div = t_div,lec_batch = batch) 
							# print(l)
							if not (l.taken_by == u):
								l.taken_by = u
							if not (l.lname == s):
								l.lname = s
							if not (l.lec_in == r):
								l.lec_in = r

							l.save()
						except:
							# print("Creating new lecture..")
							l = Lecture(lname = s, lec_day = t_day, lec_time = t, lec_div = t_div, taken_by = u, lec_in = r,lec_batch = batch)
							l.full_clean()
							l.save()




					
					# l = Lecture(lname = s, taken_by = u, lec_day = t_day, lec_time = t, lec_div = t_div)
					# if(Lecture.objects.filter(lec_day = t_day, lec_time__start_time = t.lec_time.start_time, lec_div = t_div, lec_batch__in = self.lec_batch).exclude(pk = self.id).exists() or self.__class__.objects.filter(lec_day = self.lec_day, lec_time__end_time = self.lec_time.end_time, lec_div = self.lec_div, lec_in = self.lec_in).exclude(pk = self.id).exists():))

					# batches = Batch.objects.filter(batch_of_year = t_year, batch_of_div = t_div)
					# rooms_for_lecture = list()
					# for batch in batches:
					# 	try:
					# 		# print(request.POST.get(str(t)+"-"+str(batch.batch)))
					# 		r = Room.objects.get(pk = int(request.POST.get(str(t)+"-"+str(batch.batch))))
					# 		# rooms_for_lecture.append(Room.objects.get(pk = int(request.POST.get(str(t)+"-"+str(batch.batch)))))
					# 		# print(r)
					# 		try:
					# 			lec = Lecture(lname = s, taken_by = u, lec_day = t_day, lec_time = t, lec_div = t_div, lec_in = r, lec_batch = batch)
					# 			lec.full_clean()
					# 			lec.save()
					# 		except:
					# 			# print("Already exist at same time")
					# 			errors = 'Conflicting timeslot ' + str(t)
					# 	except:
					# 		print("No ts")


						# try:
						# 	lec = Lecture.objects.get(lname = s, taken_by = u, lec_day = t_day, lec_time = t, lec_div = t_div,lec_in = r)
						# 	print(lec)
						# except:
						# 	lec = Lecture(lname = s, taken_by = u, lec_day = t_day, lec_time = t, lec_div = t_div,lec_in = r)
						# 	print("Not exist")
						# 	lec.full_clean()
						# 	try:
						# 		lec.save()
						# 		print("Success")
						# 	except Exception as e:
						# 		print("Already exist at same time")
						# 		errors = 'Conflicting timeslot ' + str(t)
						# finally:
						# 	lec.lec_batch.add(batch)
						# 	try:
						# 		lec.save()
						# 		print("Success")
						# 	except Exception as e:
						# 		print("Already exist at same time")
						# 		errors = 'Conflicting timeslot ' + str(t)



		time_slots = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff__lte=datetime.timedelta(hours = 2))

		pracs_ts = TimeSlot.objects.annotate(
	    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
		).filter(diff=datetime.timedelta(hours = 2))

		subjects = Subject.objects.all();

		batches = Batch.objects.all();

		rooms = Room.objects.all();

		context_data = {
			"errors" : errors,
			"timeslots" : time_slots,
			"pracsts" : pracs_ts,
			"subjects" : subjects,
			"batches" : batches,
			"rooms" : rooms
		}
		return render(request,'assistant/updatett.html',context_data)
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)


def get_lec(request,year,division,timeslot,day,batch):
	if request.user.is_staff:
		year = Year.objects.get(year = year)
		# print(year)
		division = Division.objects.get(division = division)
		# print(division)
		timeslot = TimeSlot.objects.get(pk = int(timeslot))
		# print(timeslot)
		day = DaysOfWeek.objects.get(day_name = day)
		# print(day)

		try:
			lectures = list()
			if(batch == 'None'):
				lecture = Lecture.objects.get(lec_day = day,lec_time = timeslot,lec_div = division,lec_batch = None ,lname__year = year)
				lectures.append(lecture)
			else:
				batch = Batch.objects.get(pk = batch)
				# print(batch)
				lecture = Lecture.objects.get(lec_day = day,lec_time = timeslot,lec_div = division,lec_batch = batch,lname__year = year)
				lectures.append(lecture)

			lec_json = serializers.serialize("json",lectures)
			# print(lec_json)
			return HttpResponse(lec_json)
		except Exception as e:
			# print("Not found")
			response = JsonResponse({"error": "Not found"})
			# response.status_code = 403
			return response
			
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)
