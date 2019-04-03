from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class TimeSlot(models.Model):
	start_time = models.TimeField(auto_now=False, auto_now_add=False)
	end_time = models.TimeField(auto_now=False, auto_now_add=False)

	def __str__(self):
		time = self.start_time.strftime("%H:%M") + " - " + self.end_time.strftime("%H:%M")
		return time

class Leave(models.Model):
    leave_note = models.TextField(blank=False, null=False)
    leave_taken_by = models.ForeignKey("auth.User",on_delete = models.CASCADE,null=True)
    approved_status = models.BooleanField(default=False, null=False)
    leave_date = models.DateField(auto_now = False,auto_now_add = False,null=True)
    leave_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE,null=True)
    def __str__(self):
    	return self.leave_taken_by.username + "@" + self.leave_date.strftime("%d/%m/%Y ")+ self.leave_time.start_time.strftime("%H:%M -") \
    	+ self.leave_time.end_time.strftime("%H:%M")
		
class DaysOfWeek(models.Model):
	day_name = models.CharField(max_length = 255,blank=False,null=False)
	def __str__(self):
		return self.day_name
		
class Subject(models.Model):
	sname = models.CharField(max_length=255,null=False,blank=False) 
	teaching_faculty = models.ManyToManyField("auth.User")

	def __str__(self):
		return self.sname


class Lecture(models.Model):
	lname = models.ForeignKey(Subject,on_delete = models.CASCADE)
	taken_by = models.ForeignKey("auth.User",on_delete = models.CASCADE)
	lec_day = models.ForeignKey(DaysOfWeek,on_delete = models.CASCADE)
	lec_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE)
	def __str__(self):
		return self.lname.sname

class LoadShift(models.Model):
	leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
	to_faculty = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="to_faculty")
	for_lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="to_lecture")
	
	# def __str__(self):
	# 	return self.to_faculty.