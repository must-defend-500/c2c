from django import forms
from django.contrib.auth.models import User
from .models import UserInfo, UserPreference

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields =[
            'first_name',
            'last_name'
        ]


#class UserPreferences
class UserPreferenceInspector(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields =[
            'inspector1',
            'inspector2',
            'inspector3',
        ]

#class UserPreferences
class UserPreferenceLender(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields =[
            'lender1',
            'lender2',
            'lender3',
        ]
#class UserPreferences
class UserPreferenceClosing(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields =[
            'closingco1',
            'closingco2',
            'closingco3',
        ]
