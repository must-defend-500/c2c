from django.contrib import admin
from .models import UserInfo, UserPreference, Contract

# Register your models here.

# class LandingPageAdmin(admin.ModelAdmin):
#     fields = ('user_id', 'first_name', 'last_name')

admin.site.register(UserInfo)
admin.site.register(UserPreference)
admin.site.register(Contract)
