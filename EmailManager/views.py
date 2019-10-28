from django.shortcuts import render
from . models import EmailLog
import threading

# Create your views here.

class EmailThread(threading.Thread):
	def __init__(self, msg):
		self.msg = msg
		threading.Thread.__init__(self)
	def run (self):
		# print("$$$$$$",self.msg.from_email,self.msg.to)
		log = self.create_log()
		self.msg.send()

		log.status = True
		log.save()
	def create_log(self):
		from_email = self.msg.from_email
		to = self.msg.to
		subject = self.msg.subject
		body = self.msg.body
		email_log = EmailLog(from_email = from_email,to = to, subject = subject, body = body)
		email_log.save()

		return email_log


def send_async_mail(msg):
	EmailThread(msg).start()