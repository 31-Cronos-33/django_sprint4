from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def error_403(request, *args, **kwargs):
    template_name = 'pages/403csrf.html'
    return render(request, template_name, status=403)


def error_404(request, *args, **kwargs):
    template_name = 'pages/404.html'
    return render(request, template_name, status=404)


def error_500(request, *args, **kwargs):
    template_name = 'pages/500.html'
    return render(request, template_name, status=500)
