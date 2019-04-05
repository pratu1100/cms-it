from django.shortcuts import HttpResponseRedirect

def index(request):
	if(request.user.is_authenticated):
		return HttpResponseRedirect('/faculty/requestleave')
	return HttpResponseRedirect('/accounts/login')