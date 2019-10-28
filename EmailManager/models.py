from django.db import models
import json
# Create your models here.

class EmailLog(models.Model):
	"""
	Model to store all the outgoing emails.
	"""
	from_email = models.EmailField(null=False)
	when = models.DateTimeField(null=False, auto_now_add=True)
	to = models.TextField(null=False)
	subject = models.CharField(null=False, max_length=128,)
	body = models.TextField(null=False)
	status = models.BooleanField(default=False)

	def set_foo(self, x):
		self.foo = json.dumps(x)

	def get_foo(self):
		return json.loads(self.foo)

	def __str__(self):
		return self.subject
