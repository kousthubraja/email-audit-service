from django.contrib import admin

from .models import EmailMessage, EmailThread


admin.site.register(EmailMessage)
admin.site.register(EmailThread)
