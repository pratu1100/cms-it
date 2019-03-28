from django.urls import path, include
from .views import create_leave

urlpatterns = [
    # path('approve/<int:leave_id>/', update_leave)
    path('requestleave/',create_leave,name="request_leave")
]
