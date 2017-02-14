# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    charge = models.TextField()
    company = models.TextField()
    user = models.ForeignKey(User,unique=True)
