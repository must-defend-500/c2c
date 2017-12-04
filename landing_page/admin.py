from django.contrib import admin
from .models import UserInfo, UserPreference, UserInvestment, FundInvestment, FundDividend, UserDividend, Fund

# Register your models here.

# class LandingPageAdmin(admin.ModelAdmin):
#     fields = ('user_id', 'first_name', 'last_name')

admin.site.register(UserInfo)
admin.site.register(UserPreference)
admin.site.register(UserInvestment)
admin.site.register(FundInvestment)
admin.site.register(FundDividend)
admin.site.register(UserDividend)
admin.site.register(Fund)
