from django.db import models
from django.utils import timezone


class Participant(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    is_test = models.BooleanField(default=False)
