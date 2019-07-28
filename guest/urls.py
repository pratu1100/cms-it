from django.urls import path
from . import views

urlpatterns = [
	path('',views.index,name="guest_index"),
	path('reserve/',views.reserve,name="reserve"),
]

