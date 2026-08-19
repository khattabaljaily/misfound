from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    country = models.ForeignKey(
        'locations.Country', on_delete=models.SET_NULL, null=True, blank=True
    )
    city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.get_full_name() or self.username
