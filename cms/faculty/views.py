from django.shortcuts import render, HttpResponseRedirect
from .models import Leave

# Update leave as approved by HOD
def update_leave(request, leave_id):  
    Leave.objects.filter(id=leave_id).update(is_approved=True)
    return HttpResponseRedirect('/hod/')
