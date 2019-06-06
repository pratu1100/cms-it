from django.contrib import admin
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift,Year,Division

# Register your models here.

class LeaveAdmin(admin.ModelAdmin):
	list_display = ('leave_taken_by','leave_start_date','leave_end_date','approved_status')
	list_display_links = ('leave_taken_by',)

admin.site.register(Leave,LeaveAdmin)

class LectureAdmin(admin.ModelAdmin):
	list_display = ('lname','taken_by','lec_day','lec_time','lec_div')
	list_display_links = ('lname',)

admin.site.register(Lecture,LectureAdmin)
admin.site.register(DaysOfWeek)
admin.site.register(TimeSlot)

admin.site.register(Subject)

class LoadShiftAdmin(admin.ModelAdmin):
# 	fields  = ('leave','to_faculty','for_lecture')
	list_display = ('leave','to_faculty','for_lecture')
	list_display_links = ('leave',)

admin.site.register(LoadShift,LoadShiftAdmin)

admin.site.register(Year)

admin.site.register(Division)

