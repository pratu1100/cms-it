from django.shortcuts import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.http import JsonResponse

def index(request):
	if(request.user.is_authenticated):
		if(request.user.is_staff):
			if(request.user.is_superuser):
				return HttpResponseRedirect('/hod/approveleaves')
			return HttpResponseRedirect('/assistant/updatett')
		return HttpResponseRedirect('/faculty')
	
	return HttpResponseRedirect('/accounts/login')

def password_change(request):
    if(request.method == 'POST'):
        old_password = request.POST.get('current_password')
        if(request.user.check_password(old_password)):
            if(request.POST.get('new_password1')==request.POST.get('new_password2')):
                request.user.set_password(request.POST.get('new_password1'))
                request.user.save()

                return JsonResponse({"success" : True})
            else:
                response =  JsonResponse({"error": "Your new passwords do not match."})
                response.status_code = 403
                return response

        else:
            response =  JsonResponse({"error": "Your old password seems to be incorrect."})
            response.status_code = 403
            return response

