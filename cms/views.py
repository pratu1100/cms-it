from django.shortcuts import HttpResponseRedirect

def index(request):
	if(request.user.is_authenticated):
		if(request.user.is_superuser):
			return HttpResponseRedirect('/hod/approveleaves')
		return HttpResponseRedirect('/faculty/requestleave')
	
	return HttpResponseRedirect('/accounts/login')
