from django.db import models

# Create your models here.
class Leave(models.Model):
    leave_note = models.CharField(max_length=255, blank=False, null=False)
    by_name = models.CharField(max_length=255, blank=False, null=False)