from django.contrib.auth.models import User
from django.db import models


class Friends(models.Model):
    library_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,
                                      related_name="library_owner")
    invited = models.EmailField(max_length=70, null=False, blank=False)

