from django.contrib import admin
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject, LoadShift

# Register your models here.
admin.site.register(Leave)
admin.site.register(Lecture)
admin.site.register(DaysOfWeek)
admin.site.register(TimeSlot)
admin.site.register(Subject)
admin.site.register(LoadShift)

