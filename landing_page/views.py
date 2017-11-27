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
from .models import UserInfo, UserPreference

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
		events = [
			{
				'title'  : 'opening date',
				'start'  : '2017-11-24',
				'color'  : 'green'
			},
			# {
			# 	title  : 'event2',
			# 	start  : '2010-01-05',
			# 	end    : '2010-01-07'
			# },
			# {
			# 	title  : 'event3',
			# 	start  : '2010-01-09T12:30:00',
			# 	allDay : false
			# }
		]
		return render(request, "calendar.html", {"html_var": True, "events": events})
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
	user = request.user
	entry = User.objects.get(username=user)
	#grab the UserInfo object in order to match UserPreference
	check_user = UserInfo.objects.filter(user_id = user)

	#User checking: if they don't exist
	if not UserInfo.objects.filter(user_id = user).exists() or not UserPreference.objects.filter(user=check_user).exists():
		#if first name and last name are not set
		if (request.method == "GET" and not UserInfo.objects.filter(user_id = user).exists()):
			form = UserInfoForm()
			return render(request, "first_login.html", {"form": form, "username": entry.username})
		#
		elif(request.method == "GET" and UserInfo.objects.filter(user_id = user).exists() and not UserPreference.objects.filter(user=check_user).exists()):
			form1 = UserPreferenceInspector()
			form2 = UserPreferenceLender()
			form3 = UserPreferenceClosing()
			return render(request, "user_preferences.html", {"html_var": True, "form1":form1, "form2":form2, "form3":form3, "username":entry.username})
		#
		elif (request.method == "POST" and not UserInfo.objects.filter(user_id = user).exists()):
			form = UserInfoForm(request.POST)
			if form.is_valid():
				#NEED TO UPDATE, not save new entry
				print("form is valid")
				UserInfo.objects.create(
					user_id = entry,
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
		elif (request.method == "POST" and UserInfo.objects.filter(user_id = user).exists() and not UserPreference.objects.filter(user=check_user).exists()):
			form1 = UserPreferenceInspector(request.POST)
			form2 = UserPreferenceLender(request.POST)
			form3 = UserPreferenceClosing(request.POST)
			if form1.is_valid() and form2.is_valid() and form3.is_valid():
				#create form
				print("form is valid")
				UserPreference.objects.create(
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
				return render(request, "upload.html", {"html_var": True, "username": entry.username})
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
		# def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			print("in test view")
			event_list = request.POST.get('data')
			print(event_list)
			data = {}
			#write a contract object
			#url = contract/164
			

			# Contract.objects.create(
			# user =
			# contract_view =
			# file_view =
			# opening_date =
			# closing_date =
			# color =
			# )

			return JsonResponse(data)


		return render(request, "upload.html", {"html_var": True, "username": entry.username})

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
















#Django Base-TemplateView
# class HomeTemplateView(TemplateView):
# 	template_name = 'landing_page.html'

# 	def get_context_data(self, *args, **kwargs):
# 		context = super(HomeTemplateView, self).get_context_data(*args, **kwargs)

# 	def get(self, request, *args, **kwargs):
# 		return render(request, "landing_page.html", {"html_var": True})
