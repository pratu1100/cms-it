from django.urls import path, include
from .views import create_leave,submit_leave

urlpatterns = [
    # path('approve/<int:leave_id>/', update_leave)
    path('requestleave/',create_leave,name="request_leave"),
  	path('requestleave/submit/<int:id>/', submit_leave, name="submit_leave")
]
