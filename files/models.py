from django.db import models
from django.conf import settings

# Create your models here.
class FileItem(models.Model):
    user                            = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    name                            = models.CharField(max_length=120, null=True, blank=True)
    path                            = models.TextField(blank=True, null=True)
    size                            = models.BigIntegerField(default=0)
    file_type                       = models.CharField(max_length=120, null=True, blank=True)
    timestamp                       = models.DateTimeField(auto_now_add=True)
    updated                         = models.DateTimeField(auto_now=True)
    uploaded                        = models.BooleanField(default=False)
    active                          = models.BooleanField(default=True)

    #@property
    def __str__(self):
        return str(self.name)
