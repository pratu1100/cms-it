from django.shortcuts import render
from faculty.models import Leave
from django.contrib.auth.decorators import login_required
from faculty.models import LoadShift,Leave

# Create your views here.
@login_required
def get_leaves(request):
	if request.user.is_superuser:
		leaves = Leave.objects.filter(approved_status = False)
		leave_loads_pairs = dict()
		for leave in leaves:
			loads_data = list()
			loads = LoadShift.objects.filter(leave = leave).values()
			for load in loads:
				loads_data.append(load)
			leave_loads_pairs[leave] = loads_data

		context_data = {
			'leave_loads_pairs' : leave_loads_pairs
		}
		print(context_data)

		return render(request, 'hod/leaves.html', context_data)