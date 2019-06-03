from django.urls import path, include
from labassistant import views

urlpatterns = [
    path('updatett/', views.get_timetable, name="updatett")
]
