from django.db import models
from rest_framework.reverse import reverse

from polls.mixins import UUIDMixin


class Participant(UUIDMixin):
    """Model to store participants info."""

    ip = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return self.ip


class Poll(UUIDMixin):
    """Model to store poll info."""

    title = models.TextField(blank=True)
    creator = models.ForeignKey(Participant, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        return reverse('poll-vote', args=(self.pk,))

    def __str__(self):
        return self.title


class Choice(UUIDMixin):
    """Model to store choices for a poll."""

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    choice = models.CharField(max_length=255)
    participants = models.ManyToManyField(Participant, blank=True, related_name='choice')

    def __str__(self):
        return f'{self.poll.title} | {self.choice}'
