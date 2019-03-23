from django.shortcuts import render
from faculty.models import Leave

# Create your views here.
def get_leaves(request):

    context = {
        'LEAVES': Leave.objects.all()
    }

    return render(request, 'hod/leaves.html', context)