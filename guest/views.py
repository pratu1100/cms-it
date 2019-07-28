from django.shortcuts import render
from faculty.models import Room
# Create your views here.
def index(request):
	if not request.user.is_authenticated:
		return render(request,"guest/guest_index.html",{})
	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)

def reserve(request):
	if not request.user.is_authenticated:
		rooms = Room.objects.filter(room = "B507")
		context_data = {
			"rooms" : rooms,
		}
		return render(request,"guest/guest_reserve.html",context_data)

	html_error_data = {
		"error_code" : "401",
		"error_message" : "UNAUTHORIZED"
	}
	return render(request,"error.html",html_error_data)