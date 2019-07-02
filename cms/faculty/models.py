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
	lec_batch = models.ForeignKey(Batch,on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return self.lname.sname

	def validate_unique(self, *args, **kwargs):
		super(Lecture,self).validate_unique(*args, **kwargs)
		# print("Hahahaha check")
		# print(self.__class__.objects.filter(lec_day = self.lec_day, lec_time__start_time = self.lec_time.start_time, lec_div = self.lec_div).exclude(pk = self.id).exists() or self.__class__.objects.filter(lec_day = self.lec_day, lec_time__end_time = self.lec_time.end_time, lec_div = self.lec_div).exclude(pk = self.id).exists())
		# print("######",self.lec_batch)
		if self.__class__.objects.filter(lec_day = self.lec_day, lec_time__start_time = self.lec_time.start_time, lec_div = self.lec_div, lec_batch = self.lec_batch).exclude(pk = self.id).exists() or self.__class__.objects.filter(lec_day = self.lec_day, lec_time__end_time = self.lec_time.end_time, lec_div = self.lec_div, lec_batch = self.lec_batch).exclude(pk = self.id).exists():
			raise ValidationError(
					message = 'Lecture with conflicting time already exists',
					code = 'unique_together'
				)
	# class Meta:
	# 	unique_together = ('lec_day','lec_time__start_time','lec_div')
	# def save(self, *args, **kwargs):
	# 	self.validate_unique(self,*args, **kwargs)
	# 	super(Lecture, self).save(*args, **kwargs)

class MakeupLecture(models.Model):
	year = models.ForeignKey(Year,on_delete = models.CASCADE)
	division = models.ForeignKey(Division,on_delete = models.CASCADE)
	lec_date = models.DateField(auto_now = False,auto_now_add = False)
	lec_subject = models.ForeignKey(Subject,on_delete = models.CASCADE)
	lec_taken_by = models.ForeignKey("auth.User",on_delete = models.CASCADE)
	lec_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE)
	lec_in = models.ForeignKey(Room,on_delete = models.CASCADE,null = True)

	def __str__(self):
		return self.lec_subject.sname

	class Meta:
		unique_together = ('year','division','lec_date','lec_time')

class IA(models.Model):
	ia_year = models.ForeignKey(Year,on_delete = models.CASCADE)
	ia_date = models.DateField(auto_now = False,auto_now_add = False)
	ia_subject = models.ForeignKey(Subject,on_delete = models.CASCADE)
	ia_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE)
	ia_in = models.ForeignKey(Room,on_delete = models.CASCADE,null = True)

	def __str__(self):
		return self.ia_subject.sname

	class Meta:
		unique_together = ('ia_year','ia_date','ia_time')

class GuestLecture(models.Model):
	lec_year = models.ForeignKey(Year,on_delete = models.CASCADE)
	lec_date = models.DateField(auto_now = False,auto_now_add = False)
	lec_subject = models.ForeignKey(Subject,on_delete = models.CASCADE)
	lec_time = models.ForeignKey(TimeSlot,on_delete = models.CASCADE)
	lec_in = models.ForeignKey(Room,on_delete = models.CASCADE,null = True)

	def __str__(self):
		return self.lec_subject.sname

	class Meta:
		unique_together = ('lec_year','lec_date','lec_time')

class OD(models.Model):
	od_type = models.CharField(max_length=20,null=False,blank=False) 
	od_title = models.CharField(max_length=255,null=False,blank=False)
	od_details = models.TextField(max_length = 255, null = False, blank = False)
	supporting_organisation = models.CharField(max_length=20,null=False,blank=False)
	from_date = models.DateField(auto_now = False,auto_now_add = False)
	to_date = models.DateField(auto_now = False,auto_now_add = False)
	last_date = models.DateField(auto_now = False,auto_now_add = False)
	fees = models.IntegerField(null=True,blank=True)
	scope = models.TextField(max_length=255,null=True,blank=True)
	correspondence = models.FileField(upload_to = 'od/correspondence/',null=True,blank=True)
	taken_by = models.ForeignKey("auth.User",on_delete= models.CASCADE)
	approved_status = models.BooleanField(default=False, null=False)

	def __str__(self):
		return self.od_type+"--"+self.od_title

	def filename(self):
		return str(self.correspondence.name).split('/')[-1]


class LoadShift(models.Model):
	leave = models.ForeignKey(Leave, on_delete=models.CASCADE,null=True,blank=True)
	to_faculty = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="to_faculty")
	for_lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="to_lecture")
	od = models.ForeignKey(OD, on_delete=models.CASCADE,null=True,blank=True)
	

	def __str__(self):
		try:
			return self.leave.leave_taken_by.username +"--"+self.to_faculty.username
		except:
			return self.od.taken_by.username +"--"+self.to_faculty.username
		else:
			return "Unknown"
