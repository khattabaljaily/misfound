from django.shortcuts import render

from apps.locations.models import City, Country
from apps.reports.models import Category, Report


def home(request):
    latest_lost = Report.objects.filter(status=Report.OPEN, type=Report.LOST).select_related('category', 'city')[:4]
    latest_found = Report.objects.filter(status=Report.OPEN, type=Report.FOUND).select_related('category', 'city')[:4]
    return render(request, 'core/home.html', {
        'latest_lost': latest_lost,
        'latest_found': latest_found,
        'categories': Category.objects.all(),
    })


def about(request):
    stats = {
        'cities': City.objects.count(),
        'countries': Country.objects.count(),
        'resolved': Report.objects.filter(status=Report.RESOLVED).count(),
    }
    return render(request, 'core/about.html', {'stats': stats})


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms(request):
    return render(request, 'core/terms.html')
