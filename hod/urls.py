from django.urls import path, include
from hod import views

urlpatterns = [
	path('', views.index, name="hod_index"),
    path('approveleaves/', views.get_leaves, name="leaves"),
    path('approveods/',views.get_ods,name = "approve_ods")
]
