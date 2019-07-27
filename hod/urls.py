from django.urls import path, include
from hod import views

urlpatterns = [
	path('', views.index, name="hod_index"),
	path('leaves',views.leave_history,name="leave_history"),
    path('approveleaves/', views.get_leaves, name="leaves"),
    path('approveods/',views.get_ods,name = "approve_ods")
]
