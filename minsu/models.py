from django.conf import settings
from django.db import models
from django.utils import timezone


def directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.id, filename)


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    finish = models.BooleanField()
    music_file = models.FileField(upload_to=directory_path, null=True)

    def __str__(self):
        return self.id

    def check_finish(self):
        return self.finish
