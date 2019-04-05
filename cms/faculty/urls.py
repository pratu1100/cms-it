from django.urls import path, include
from .views import create_leave,submit_leave,submit_load_shift

urlpatterns = [
    # path('approve/<int:leave_id>/', update_leave)
    path('requestleave/',create_leave,name="request_leave"),
  	path('requestleave/submit/', submit_leave, name="submit_leave"),
  	path('requestleave/submit/loadshift/',submit_load_shift,name="loadshifts")
]
