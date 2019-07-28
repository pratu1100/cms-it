from django.contrib import admin
from .models import Reservation

# Register your models here.

class ReservationAdmin(admin.ModelAdmin):
	list_display = ('contact_person','institute','department','date','start_time')
	list_display_links = ('contact_person',)