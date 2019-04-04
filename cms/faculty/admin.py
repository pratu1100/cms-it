from django.contrib import admin
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift

# Register your models here.
admin.site.register(Leave)
admin.site.register(Lecture)
admin.site.register(DaysOfWeek)
admin.site.register(TimeSlot)
admin.site.register(Subject)

class LoadShiftAdmin(admin.ModelAdmin):
# 	fields  = ('leave','to_faculty','for_lecture')
	list_display = ('leave','to_faculty','for_lecture')
	list_display_links = ('leave',)

admin.site.register(LoadShift,LoadShiftAdmin)


