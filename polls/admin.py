from django.contrib import admin
from polls.models import Participant, Poll, Choice

admin.site.register(Participant)
admin.site.register(Poll)
admin.site.register(Choice)
