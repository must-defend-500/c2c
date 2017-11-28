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

from .forms import UserInfoForm, UserPreferenceInspector, UserPreferenceLender, UserPreferenceClosing
from .models import UserInfo, UserPreference, Contract

import datetime
import json
import random

# Create your views here.

# def home(request):
# 	return render(request, "landing_page.html", {"html_var": True})

class ContractCreation(APIView):
	def post(self, request, *args, **kwargs):
		data = {}
		return Response(data, status=status.HTTP_200_OK)

class test(View):
	def post(self, request, *args, **kwargs):
		print("in test view")
		data = {"nick": "andrew"}
		#return Response(data, status=status.HTTP_200_OK)
		return JsonResponse(data)

class CalendarView(View):
	def get(self, request, *args, **kwargs):
		user = request.user.id
		events = []
			#for current user, get all the contract objects, and for each date, add to events
		contracts = Contract.objects.filter(user=user)
		for contract in contracts:
			title_var = str(contract.contract_num)
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

		return render(request, "calendar.html", {"html_var": True, "events": events})

class ContractView(View):
	def get(self, request, *args, **kwargs):
		user = request.user.id
		contracts = Contract.objects.filter(user=user)

		return render(request, "landing_page.html", {"html_var": True})


#Django Base-View
class HomeView(View):
	def get(self, request, *args, **kwargs):
		return render(request, "landing_page.html", {"html_var": True})


#Django view for the profile page
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
			data = {}
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
			color = color_contract
			)

			return JsonResponse(data)

		#for current user, get all the contract objects, and for each date, add to events
		contracts = Contract.objects.filter(user=user)
		events = []
		contract_urls = []
		for contract in contracts:
			contract_urls.append(contract.file_view)
			title_var = str(contract.contract_num)
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

		print(contract_urls)
		return render(request, "upload.html", {"html_var": True, "username": entry.username, "events": events})

	#document upload

#Pass returned upload information to django backend and create Contract object


#version1: a class-based view

# class ProfileView(LoginRequiredMixin, View):
# 	#check if username's first and lastname have been set, otherwise re-direct user to profile form
#
# 	form = NamesCreateForm()
#
# 	def get(self, request, *args, **kwargs):
# 		user = self.request.user
#
# 		entry = User.objects.get(username=user)
#
# 		lastname = entry.last_name
# 		firstname = entry.first_name
# 		if lastname == "" or firstname == "":
# 			return render(request, "first_login.html", {"form": form})
# 		else:
# 			return render(request, "profile.html", {"html_var": True})
# 	def post(self, request, *args, **kwargs):
# 		#post first and last name to django database
# 		form = NamesCreateForm(request.POST)
# 		if form.is_valid():
# 			print('valid')
# 			# obj=form.save(commit=False)
# 			# obj.save()
# 			# User.objects.create(first_name='nick', last_name='murray')
#
# 			return render(request, "profile.html", {"html_var": True})
# 		else:
# 			print('not valid')
# 			return render(request, "first_login.html", {"form": form})
