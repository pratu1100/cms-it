from django.urls import path, include
from labassistant import views

urlpatterns = [
    path('updatett/', views.get_timetable, name="updatett"),
    path('getlecture/<str:year>/<str:division>/<str:timeslot>/<str:day>/<str:batch>',views.get_lec, name="getlecture"),
    path('getpreviewlink/', views.get_preview_link, name="getpreviewlink")
]
