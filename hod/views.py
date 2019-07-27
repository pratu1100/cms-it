from django.shortcuts import render,HttpResponseRedirect
from faculty.models import Leave
from django.contrib.auth.decorators import login_required
from faculty.models import LoadShift,Leave, OD
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User


# Create your views here.
@login_required
def index(request):
	if request.user.is_superuser:
		return HttpResponseRedirect('/hod/approveleaves')

@login_required
def get_leaves(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			leave = Leave.objects.get(pk = request.POST.get('leave_id'))
			if '_reject' in request.POST:

				subject = 'Leave Notification'
						
				message_data = {
					'leave' : leave,
				}

				email_from = settings.EMAIL_HOST_USER
				recipient_list = []
				recipient_list.append(leave.leave_taken_by.email)
				html_content = render_to_string('email/approve_notification.html', message_data) # render with dynamic value
				text_content = strip_tags(html_content)

				msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
				msg.attach_alternative(html_content, "text/html")
				
				msg.send()
				
				leave.delete()
				
			elif '_approve' in request.POST:
				leave.approved_status = True
				leave.save() 

				subject = 'Leave Notification'
						
				message_data = {
					'leave' : leave,
				}

				email_from = settings.EMAIL_HOST_USER
				recipient_list = []
				recipient_list.append(leave.leave_taken_by.email)
				html_content = render_to_string('email/approve_notification.html', message_data) # render with dynamic value
				text_content = strip_tags(html_content)

				msg = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
				msg.attach_alternative(html_content, "text/html")
				
				msg.send()

		leaves = Leave.objects.filter(approved_status = None)
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
		# print(context_data)

		return render(request, 'hod/leaves.html', context_data)

@login_required
def get_ods(request):
	if request.user.is_superuser:
		if request.method == 'POST':
			od = OD.objects.get(pk = request.POST.get('od_id'))
			if '_reject' in request.POST:
				od.delete()	
			elif '_approve' in request.POST:
				od.approved_status = True
				od.save()
		ods = OD.objects.filter(approved_status = False)
		od_loads_pairs = list()
		for od in ods:
			loads_data = list()
			loads = LoadShift.objects.filter(od = od)
			for load in loads:
				loads_data.append(load)
			od_loads_pairs.append((od,loads_data))

		context_data = {
			"od_loads_pairs" : od_loads_pairs,
		}
		return render(request, 'hod/approve_ods.html', context_data)

