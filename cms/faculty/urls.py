from django.urls import path, include
from .views import create_leave,submit_leave,submit_load_shift,get_makeup,post_makeup,get_ia,post_ia,get_timeslots,get_available_rooms,guestlecture,guestlecture_schedule,od

urlpatterns = [
    # path('approve/<int:leave_id>/', update_leave)
    path('requestleave/',create_leave,name="request_leave"),
  	path('requestleave/submit/', submit_leave, name="submit_leave"),
  	path('requestleave/submit/loadshift/',submit_load_shift,name="loadshifts"),
  	path('makeup/',get_makeup,name="makeup"),
  	path('makeup/reserve',post_makeup,name="reserve"),
  	path('ia/',get_ia,name="IA"),
  	path('ia/post',post_ia,name="postia"),
  	# path('subjects/<int:yid>/',get_subjects,name="get_subjects")
  	path('timeslots/<str:syear>/<str:sdate>',get_timeslots,name="get_timeslots"),
  	path('rooms/available/<str:sdate>/<str:slot>',get_available_rooms,name="available_rooms"),
  	path('guestlecture/',guestlecture,name="guestlecture"),
  	path('guestlecture/schedule',guestlecture_schedule,name="guestlecture_schedule"),
    path('od/',od,name="od")
]
