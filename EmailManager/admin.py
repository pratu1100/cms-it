from django.contrib import admin
from .models import EmailLog
# Register your models here.

class EmailLogAdmin(admin.ModelAdmin):
	list_display = ('subject','status')
	list_display_links = ('subject',)

admin.site.register(EmailLog,EmailLogAdmin)