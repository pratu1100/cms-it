from django.db import models
from faculty.models import Room
# Create your models here.
class Reservation(models.Model):
	room = models.ForeignKey(Room,on_delete = models.CASCADE,default = 18)
	email = models.CharField(max_length=255,null=False,blank=False)
	contact_person = models.CharField(max_length=255,null=False,blank=False)
	institute = models.CharField(max_length=255,null=False,blank=False)
	department = models.CharField(max_length=255,null=True,blank=True)
	purpose = models.TextField(null=True,blank=True)
	start_date = models.DateField(auto_now = False,auto_now_add = False)
	end_date = models.DateField(auto_now = False,auto_now_add = False)
	start_time = models.TimeField(auto_now = False,auto_now_add = False)
	end_time = models.TimeField(auto_now = False,auto_now_add = False)

	def __str__(self):
		return self.contact_person