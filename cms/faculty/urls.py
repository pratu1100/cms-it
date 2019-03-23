from django.urls import path, include
from .views import update_leave

urlpatterns = [
    path('approve/<int:leave_id>/', update_leave)
]
