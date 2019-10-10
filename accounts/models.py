from django.db import models
from django.contrib.auth.models import User


class UserActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=36)
