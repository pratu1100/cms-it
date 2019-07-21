from django.shortcuts import HttpResponseRedirect

def index(request):
	if(request.user.is_authenticated):
		if(request.user.is_staff):
			if(request.user.is_superuser):
				return HttpResponseRedirect('/hod/approveleaves')
			return HttpResponseRedirect('/assistant/updatett')
		return HttpResponseRedirect('/faculty')
	
	return HttpResponseRedirect('/accounts/login')
