from django.urls import path, include
from hod import views

urlpatterns = [
    path('', views.get_leaves, name="Leaves")
]
