from django.urls import path, include
from hod import views

urlpatterns = [
    path('approveleaves/', views.get_leaves, name="leaves")
]
