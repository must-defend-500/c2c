from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.forms import ModelForm
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core import serializers
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from .forms import UserInfoForm, SendUserPayment, FirstInfoForm
from .models import UserInfo, UserPreference, Fund, UserInvestment, FundDividend

import datetime
import json
import random

# Create your views here.

dict_funds = {
'REIT': '0',
'BioTech': '1',
'Tech': '2',
'Crypto': '3'
}

class ChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, *args, **kwargs):
		fund = self.kwargs['fund']
		fund_entry = dict_funds[fund]
		entry = Fund.objects.get(category=fund_entry)

		labels = ["USD", "BTC", "ETH", "LTC", "Investments"]
		value = [float(entry.cash_amount), float(entry.BTC_amount), float(entry.ETH_amount), float(entry.LTC_amount), float(entry.investment_value)]

		labels2 = []
		value2 = []

		dividend_entries = FundDividend.objects.filter(payee=entry).order_by('dividend_date')

		for dividend in dividend_entries:
			print(dividend.dividend_amount)
			value2.append(dividend.dividend_amount)
			labels2.append(str(dividend.dividend_date))

		data = {"labels": labels, "fund_data": value, "labels2": labels2, "fund_data2": value2}

		return JsonResponse(data, safe=False)

class MainPageData(APIView):

	data = {}
	return JsonResponse(data, safe=False)

#Django Base-View
class ViewFund(View):
	def get(self, request, *args, **kwargs):
		fund = self.kwargs['fund']
		form = SendUserPayment()
		fund_entry = dict_funds[fund]
		entry = Fund.objects.get(category=fund_entry)
		net_asset = entry.net_asset_value
		#get the fund info passed from the url
		return render(request, "viewfund.html", {"html_var": True, "fund":fund, "form":form, "net_asset":net_asset})
	def post(self, request, *args, **kwargs):
		fund = self.kwargs['fund']
		fund_entry = dict_funds[fund]
		entry = Fund.objects.get(category=fund_entry)
		username = request.user
		form = SendUserPayment(request.POST or None)
		print(entry)
		if form.is_valid():
			amount_invested = form.cleaned_data.get('amount')
			UserInvestment.objects.create(
					user = username,
					currency = '0',
					fund_category = entry,
					amount = amount_invested
			)

			# entry.save(update_field=['BTC_amount'+amount_invested])
			entry.BTC_amount += amount_invested
			entry.net_asset_value += 11800*amount_invested
			entry.save()

		form = SendUserPayment()
		net_asset = entry.net_asset_value
		return render(request, "viewfund.html", {"html_var": True, "fund":fund, "form":form,"net_asset":net_asset})

class ViewAccount(View):
	def get(self, request, *args, **kwargs):
		username = request.user
		entry = UserInfo.objects.get(user_id=username)
		form = UserInfoForm(instance=entry)
		#display model form
		return render(request, "account.html", {"html_var": True, "form": form, "username":username})
	def post(self, request, *args, **kwargs):
		username = request.user
		entry = UserInfo.objects.get(user_id=username)
		form = UserInfoForm(request.POST  or None, instance = entry)
		if form.is_valid():
			form.save()
		form = UserInfoForm(instance=entry)
		success = "You have successfully updated your account info!"
		return render(request, "account.html", {"html_var": True, "form":form, "username":username, "success":success})

class CalendarView(View):
	def get(self, request, *args, **kwargs):
		user = request.user.id
		username1 = request.user
		entry = User.objects.get(username=username1)
		events = []
			#for current user, get all the contract objects, and for each date, add to events
		contracts = Contract.objects.filter(user=user)
		for contract in contracts:
			value = [contract.contract_num, contract.street, contract.color, contract.file_view]
			title_var = str(contract.street)
			contractdate = {
				'title': "Contract "+ title_var + ": "+ "Contract Date",
				'start': str(contract.opening_date),
				'color': contract.color,
			}
			events.append(contractdate)
			closingdate = {
					'title': "Contract "+ title_var + ": "+ "Closing Date",
					'start': str(contract.closing_date),
					'color': contract.color,
			}
			events.append(closingdate)

		return render(request, "calendar.html", {"html_var": True, "events": events, "username":entry.username})

#Django Base-View
class HomeView(View):
	def get(self, request, *args, **kwargs):
		return render(request, "landing_page.html", {"html_var": True})


#django view for the profile page
class UserProfile(View):
	def get(self, request, *args, **kwargs):
		return render(request, "profile.html", {"html_var": True})

#version3: new profile view with UserInfoForm
def profile_view (request):
	user = request.user.id
	username1 = request.user
	entry = User.objects.get(username=username1)
	#grab the UserInfo object in order to match UserPreference

	#User checking: if they don't exist
	if not UserInfo.objects.filter(user = user).exists():
		#if first name and last name are not set
		if (request.method == "GET" and not UserInfo.objects.filter(user = user).exists()):
			form = FirstInfoForm()
			return render(request, "first_login.html", {"form": form, "username": entry.username})
		#
		elif (request.method == "POST" and not UserInfo.objects.filter(user = user).exists()):
			form = FirstInfoForm(request.POST)
			if form.is_valid():
				#NEED TO UPDATE, not save new entry
				UserInfo.objects.create(
					user = entry,
					user_email = entry.email,
					last_name = form.cleaned_data.get('last_name'),
					first_name = form.cleaned_data.get('first_name'),
					wallet = form.cleaned_data.get('wallet')
				)
				return render(request, "upload.html", {"html_var": True, "username": entry.username})
			else:
				print("Form is not valid")
				#print(form.errors)
				return render(request,  "first_login.html", {"form": form, "username": entry.username})

	#if new contract is created on homepage
	else:
		return render(request, "upload.html", {"html_var": True, "username": entry.username})
