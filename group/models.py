from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    admin = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='group')

    def __str__(self):
        return self.name


class Message(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('timestamp',)
