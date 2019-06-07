from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

class Year(models.Model):
	year = models.CharField(max_length=255,null=False,blank=False) 

	def __str__(self):
		return self.year

class Division(models.Model):
	division = models.CharField(max_length=255,null=False,blank=False) 
	div_of = models.ForeignKey(Year,on_delete="models.CASCADE",null=True)

	def __str__(self):
		return self.division

class Batch(models.Model):
	batch = models.CharField(max_length=255,null=False,blank=False)
	batch_of_year = models.ForeignKey(Year,on_delete="models.CASCADE",null=True)
	batch_of_div = models.ForeignKey(Division,on_delete="models.CASCADE",null=True)
	
	def __str__(self):
		return str(self.batch_of_year) + " - " + str(self.batch_of_div) + " - " + str(self.batch)

class Room(models.Model):
	room = models.CharField(max_length=255,null=False,blank=False)

	def __str__(self):
		return self.room

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
    leave_start_date = models.DateField(auto_now = False,auto_now_add = False,)
    leave_end_date = models.DateField(auto_now = False,auto_now_add = False,)
    # leave_start_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE,null=True)
    leave_start_time = models.TimeField(auto_now=False,auto_now_add=False)
    leave_end_time = models.TimeField(auto_now=False,auto_now_add=False)


    def __str__(self):
    	# print(self.leave_taken_by.username + "@" + self.leave_start_date.strftime("%d/%m/%Y ")+ self.leave_time.start_time.strftime("%H:%M -"))
    	
    	return self.leave_taken_by.username + "@" + self.leave_start_date.strftime("%d/%m/%Y")+ "--"+self.leave_start_time.strftime("%H:%M")

class DaysOfWeek(models.Model):
	day_name = models.CharField(max_length = 255,blank=False,null=False)
	def __str__(self):
		return self.day_name
		
class Subject(models.Model):
	sname = models.CharField(max_length=255,null=False,blank=False) 
	teaching_faculty = models.ManyToManyField("auth.User")
	year = models.ForeignKey(Year,on_delete="models.CASCADE",null=True)

	def __str__(self):
		return self.sname

class Lecture(models.Model):
	lname = models.ForeignKey(Subject,on_delete = models.CASCADE)
	taken_by = models.ForeignKey("auth.User",on_delete = models.CASCADE)
	lec_day = models.ForeignKey(DaysOfWeek,on_delete = models.CASCADE)
	lec_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE)
	lec_div = models.ForeignKey(Division,on_delete= models.CASCADE,null=True)
	lec_in = models.ForeignKey(Room,on_delete= models.CASCADE,null=True)
	lec_batch = models.ManyToManyField(Batch)

	def __str__(self):
		return self.lname.sname

	def validate_unique(self, *args, **kwargs):
		super(Lecture,self).validate_unique(*args, **kwargs)
		print("Hahahaha check")
		print(self.__class__.objects.filter(lec_day = self.lec_day, lec_time__start_time = self.lec_time.start_time, lec_div = self.lec_div).exclude(pk = self.id).exists() or self.__class__.objects.filter(lec_day = self.lec_day, lec_time__end_time = self.lec_time.end_time, lec_div = self.lec_div).exclude(pk = self.id).exists())
		if self.__class__.objects.filter(lec_day = self.lec_day, lec_time__start_time = self.lec_time.start_time, lec_div = self.lec_div).exclude(pk = self.id).exists() or self.__class__.objects.filter(lec_day = self.lec_day, lec_time__end_time = self.lec_time.end_time, lec_div = self.lec_div).exclude(pk = self.id).exists():
			raise ValidationError(
					message = 'Lecture with conflicting time already exists',
					code = 'unique_together'
				)
	# class Meta:
	# 	unique_together = ('lec_day','lec_time__start_time','lec_div')
	def save(self, *args, **kwargs):
		self.validate_unique(self,*args, **kwargs)
		super(Lecture, self).save(*args, **kwargs)


class LoadShift(models.Model):
	leave = models.ForeignKey(Leave, on_delete=models.CASCADE)
	to_faculty = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="to_faculty")
	for_lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="to_lecture")
	
	def __str__(self):
		return self.leave.leave_taken_by.username +"--"+self.to_faculty.username
