from django.urls import path, include
from .views import create_leave,submit_leave,submit_load_shift,get_makeup,post_makeup,get_ia,post_ia,get_timeslots

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
  	path('timeslots/<str:syear>/<str:sdate>',get_timeslots,name="get_timeslots")

]
