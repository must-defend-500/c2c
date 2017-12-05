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

from .forms import UserInfoForm, UserPreferenceInspector, UserPreferenceLender, UserPreferenceClosing, SendUserPayment
from .models import UserInfo, UserPreference, Fund, UserInvestment

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

		labels2 = ["Hey"]
		value2 = [50]

		data = {"labels": labels, "fund_data": value, "labels2": labels2, "fund_data2": value2}

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
	if not UserInfo.objects.filter(user = user).exists() or not UserPreference.objects.filter(user=user).exists():
		#if first name and last name are not set
		if (request.method == "GET" and not UserInfo.objects.filter(user = user).exists()):
			form = UserInfoForm()
			return render(request, "first_login.html", {"form": form, "username": entry.username})
		#
		elif(request.method == "GET" and UserInfo.objects.filter(user = user).exists() and not UserPreference.objects.filter(user=user).exists()):
			form1 = UserPreferenceInspector()
			form2 = UserPreferenceLender()
			form3 = UserPreferenceClosing()
			return render(request, "user_preferences.html", {"html_var": True, "form1":form1, "form2":form2, "form3":form3, "username":entry.username})
		#
		elif (request.method == "POST" and not UserInfo.objects.filter(user = user).exists()):
			form = UserInfoForm(request.POST)
			if form.is_valid():
				#NEED TO UPDATE, not save new entry
				UserInfo.objects.create(
					user = entry,
					user_email = entry.email,
					last_name = form.cleaned_data.get('last_name'),
					first_name = form.cleaned_data.get('first_name')
				)
				form1 = UserPreferenceInspector()
				form2 = UserPreferenceLender()
				form3 = UserPreferenceClosing()
				return render(request, "user_preferences.html", {"html_var": True, "form1":form1, "form2":form2, "form3":form3, "username":entry.username})
			else:
				print("Form is not valid")
				#print(form.errors)
				return render(request,  "first_login.html", {"form": form, "username": entry.username})
		elif (request.method == "POST" and UserInfo.objects.filter(user = user).exists() and not UserPreference.objects.filter(user=user).exists()):
			form1 = UserPreferenceInspector(request.POST)
			form2 = UserPreferenceLender(request.POST)
			form3 = UserPreferenceClosing(request.POST)
			if form1.is_valid() and form2.is_valid() and form3.is_valid():
				#create form
				print("form is valid")
				UserPreference.objects.create(
					user = entry,
					inspector1 = form1.cleaned_data.get('inspector1'),
					inspector2 = form1.cleaned_data.get('inspector2'),
					inspector3 = form1.cleaned_data.get('inspector3'),

					lender1 = form2.cleaned_data.get('lender1'),
					lender2 = form2.cleaned_data.get('lender2'),
					lender3 = form2.cleaned_data.get('lender3'),

					closingco1 = form3.cleaned_data.get('closingco1'),
					closingco2 = form3.cleaned_data.get('closingco2'),
					closingco3 = form3.cleaned_data.get('closingco3'),
				)
				events1 = []
				return render(request, "upload.html", {"html_var": True, "username": entry.username, "events":events1})
			#if form is not valid
			else:
				print("Form is not valid")
				form1 = UserPreferenceInspector()
				form2 = UserPreferenceLender()
				form3 = UserPreferenceClosing()
				return render(request, "user_preferences.html", {"html_var": True, "form1":form1, "form2":form2, "form3":form3, "username":entry.username})

	#if new contract is created on homepage
	else:
		# NEED TO FIGURE OUT CSRF shit
		if request.method == 'POST':
			#and request.POST.get('data')
			print(request.POST.get('data'))
			event_list = request.POST.get('data')
			jsonData = json.loads(event_list)

			file1 = jsonData['contract_view_url']
			#handle converting date of mm/dd/yyyy to datetime
			json_date1 = jsonData['firstDate']
			json_date2 = jsonData['closing_date']

			if json_date1.count("/")==2:
				date1 = (datetime.datetime.strptime(json_date1, '%m/%d/%Y').date())
			elif json_date1.count("/")==1:
				date1 = (datetime.datetime.strptime(json_date1, '%m/%d%Y').date())

			if json_date2.count("/")==2:
				date2 = (datetime.datetime.strptime(json_date2, '%m/%d/%Y').date())
			elif json_date2.count("/")==1:
				date2 = (datetime.datetime.strptime(json_date2, '%m/%d%Y').date())

			user_contract = jsonData['user_contract']
			street_address = jsonData['street']

			#write a contract object
			#url = contract/164

			r = lambda: random.randint(0,255)
			color_contract = '#%02X%02X%02X' % (r(),r(),r())

			Contract.objects.create(
			user = entry,
			contract_view = user_contract,
			file_view = file1,
			opening_date = date1,
			closing_date = date2,
			color = color_contract,
			street = street_address,
			)
			contracts = Contract.objects.filter(user=user).values('contract_view', 'street', 'contract_num', 'opening_date', 'closing_date', 'color')

			serialized_q = json.dumps(list(contracts), cls=DjangoJSONEncoder)
			data = serialized_q

			return JsonResponse(data, safe=False)


		return render(request, "upload.html", {"html_var": True, "username": entry.username})

#Pass returned upload information to django backend and create Contract object
