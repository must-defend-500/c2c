"""c2c URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView

from landing_page.views import HomeView, profile_view, ViewFund, ViewAccount, ChartData
from files.views import FilePolicyAPI, FileUploadCompleteHandler, ViewFile

urlpatterns = [
    #need to authorize these properly
    url(r'^upload/$', TemplateView.as_view(template_name='upload.html'), name='upload-home'),
    #capture this url in order to
    url(r'^funds/(?P<fund>REIT|Crypto|Tech|BioTech)/$', ViewFund.as_view()),
    url(r'^api/charts/(?P<fund>REIT|Crypto|Tech|BioTech)/$', ChartData.as_view()),
    url(r'^viewfile$', ViewFile.as_view()),
    url(r'^account$', ViewAccount.as_view()),
    #/c2c.ai/44/
    url(r'^(?P<username>[\w.@+-]+/\d{1,5}/)$', ViewFile.as_view()),
    url(r'^api/files/complete/$', FileUploadCompleteHandler.as_view(), name='upload-complete'),
    url(r'^api/files/policy/$', FilePolicyAPI.as_view(), name='upload-policy'),
    url(r'^admin/', admin.site.urls),
    url(r'^profile', profile_view),
    url(r'^$', HomeView.as_view()),
	url(r'^accounts/', include('allauth.urls')),
]
