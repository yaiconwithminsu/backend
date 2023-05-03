from django.conf import settings
from django.db import models
from django.utils import timezone


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    is_upload = models.BooleanField()

    def upload(self):
        self.save()

    def __str__(self):
        return self.id
