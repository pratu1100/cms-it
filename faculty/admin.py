from django.contrib import admin
from .models import Leave,Lecture,DaysOfWeek,TimeSlot,Subject,LoadShift,Year,Division,Room,Batch,MakeupLecture,IA,GuestLecture,OD,LeaveType, IaBatchRoomMapping

# Register your models here.

class LeaveAdmin(admin.ModelAdmin):
	list_display = ('leave_taken_by','leave_type','leave_start_date','leave_end_date','approved_status')
	list_display_links = ('leave_taken_by',)

admin.site.register(Leave,LeaveAdmin)

class LectureAdmin(admin.ModelAdmin):
	list_display = ('lname','taken_by','lec_day','lec_time','lec_div','lec_in')
	list_display_links = ('lname',)

admin.site.register(Room)

class BatchAdmin(admin.ModelAdmin):
	list_display = ('batch','batch_of_year','batch_of_div')
	list_display_links = ('batch',)

admin.site.register(Batch,BatchAdmin)


admin.site.register(Lecture,LectureAdmin)
# admin.site.register(DaysOfWeek)
# admin.site.register(TimeSlot)

admin.site.register(Subject)

class LoadShiftAdmin(admin.ModelAdmin):
# 	fields  = ('leave','to_faculty','for_lecture')
	list_display = ('leave','od','for_lecture','approved_status')
	list_display_links = ('leave','od')

admin.site.register(LoadShift,LoadShiftAdmin)

admin.site.register(Year)

admin.site.register(Division)

class MakeupAdmin(admin.ModelAdmin):
	list_display = ('lec_subject','lec_taken_by','lec_date','lec_time')
	list_display_links = ('lec_subject',)

admin.site.register(MakeupLecture, MakeupAdmin)

class IaAdmin(admin.ModelAdmin):
	list_display = ('ia_subject','ia_date','ia_year')
	list_display_links = ('ia_subject',)

admin.site.register(IA,IaAdmin)

class IaBatchRoomMappingAdmin(admin.ModelAdmin):
	list_display = ('ia','batch','room','supervisor')
	list_display_links = ('ia',)

admin.site.register(IaBatchRoomMapping,IaBatchRoomMappingAdmin)

class GuestLectureAdmin(admin.ModelAdmin):
	list_display = ('lec_subject','lec_date','lec_time','lec_year','lec_in','title')
	list_display_links = ('lec_subject',)

admin.site.register(GuestLecture,GuestLectureAdmin)

class ODAdmin(admin.ModelAdmin):
	list_display = ('od_title','od_type','taken_by','approved_status')
	list_display_links = ('od_title',)

admin.site.register(OD,ODAdmin)
# admin.site.register(LeaveType)	