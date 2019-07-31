from django.urls import path
from . import views

urlpatterns = [
	path('',views.index,name="guest_index"),
	path('reserve/',views.reserve,name="reserve"),
	path('api/timeslots',views.get_timeslots,name="apitimeslots"),
	path('events/',views.events,name="view_events")
]

