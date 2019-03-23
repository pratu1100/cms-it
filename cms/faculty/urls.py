from django.urls import path, include
from faculty import views

urlpatterns = [
    path('', views.index)
]
