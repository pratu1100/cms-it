from django.shortcuts import render
from faculty.models import Leave
from django.contrib.auth.decorators import login_required
from faculty.models import LoadShift,Leave

# Create your views here.
@login_required
def get_leaves(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			leave = Leave.objects.get(pk = request.POST.get('leave_id'))
			if '_reject' in request.POST:
				leave.delete()	
			elif '_approve' in request.POST:
				leave.approved_status = True
				leave.save() 

		leaves = Leave.objects.filter(approved_status = False)
		leave_loads_pairs = list()
		for leave in leaves:
			loads_data = list()
			loads = LoadShift.objects.filter(leave = leave)
			for load in loads:
				loads_data.append(load)
			leave_loads_pairs.append((leave,loads_data))

		context_data = {
			'leave_loads_pairs' : leave_loads_pairs
		}
		print(context_data)

		return render(request, 'hod/leaves.html', context_data)
