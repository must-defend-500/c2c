from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class UserInfo(models.Model):
    #change this to settings.AUTH_USER_MODEL.id
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    # user_id = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    user_email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user_id.username

class UserPreference(models.Model):
    user = models.ForeignKey(UserInfo, to_field='user_id', primary_key=True, on_delete=models.CASCADE)
    inspector_tup = (
    ('0', 'BPG Home Inspectors'),
    ('1', 'inspect_B'),
    ('2', 'inspect_C'),
    ('3', 'inspect_D'),
    ('4', 'inspect_E'),
    )

    inspector1 = models.CharField(max_length=1, choices = inspector_tup)
    inspector2 = models.CharField(max_length=1, choices = inspector_tup)
    inspector3 = models.CharField(max_length=1, choices = inspector_tup)

    lender_tup = (
    ('0', 'USA Mortgage'),
    ('1', 'lender_B'),
    ('2', 'lender_C'),
    ('3', 'lender_D'),
    ('4', 'lender_E'),
    )

    lender1 = models.CharField(max_length=1, choices = lender_tup)
    lender2 = models.CharField(max_length=1, choices = lender_tup)
    lender3 = models.CharField(max_length=1, choices = lender_tup)

    closingco_tup = (
    ('0', 'Investors Title'),
    ('1', 'closingco_B'),
    ('2', 'closingco_C'),
    ('3', 'closingco_D'),
    ('4', 'closingco_E'),
    )

    closingco1 = models.CharField(max_length=1, choices = closingco_tup)
    closingco2 = models.CharField(max_length=1, choices = closingco_tup)
    closingco3 = models.CharField(max_length=1, choices = closingco_tup)

    def __str__(self):
        return str(self.user)

class Contract(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.ForeignKey(UserInfo, to_field='user_id', primary_key=True, on_delete=models.CASCADE)
    #path = models.TextField(blank=True, null=True)
    contract_view = models.URLField() #/contract/164
    file_view = models.URLField() #viewing the actual contract /username/164/164.[df]
    opening_date = models.DateField(auto_now=False, auto_now_add=False)
    closing_date = models.DateField(auto_now=False, auto_now_add=False)
    color = models.CharField(max_length = 15)

    def __str__(self):
        return str(self.contract_view)

#
# class CalenderEvents(models.Model):
