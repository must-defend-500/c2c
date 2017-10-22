from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

# Create your views here.

# def home(request):
# 	return render(request, "landing_page.html", {"html_var": True})


#Django Base-View
class HomeView(View):
	def get(self, request, *args, **kwargs):
		return render(request, "landing_page.html", {"html_var": True})


#Django Base-TemplateView
# class HomeTemplateView(TemplateView):
# 	template_name = 'landing_page.html'
	
# 	def get_context_data(self, *args, **kwargs):
# 		context = super(HomeTemplateView, self).get_context_data(*args, **kwargs)

# 	def get(self, request, *args, **kwargs):
# 		return render(request, "landing_page.html", {"html_var": True})