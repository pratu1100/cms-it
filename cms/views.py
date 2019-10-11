from django.shortcuts import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

def index(request):
	if(request.user.is_authenticated):
		if(request.user.is_staff):
			if(request.user.is_superuser):
				return HttpResponseRedirect('/hod/approveleaves')
			return HttpResponseRedirect('/assistant/updatett')
		return HttpResponseRedirect('/faculty')
	
	return HttpResponseRedirect('/accounts/login')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponse("success")
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {
        'form': form
    })
