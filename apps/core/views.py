from django.shortcuts import render

from apps.reports.models import Report


def home(request):
    latest_lost = Report.objects.filter(status=Report.OPEN, type=Report.LOST).select_related('category', 'city')[:6]
    latest_found = Report.objects.filter(status=Report.OPEN, type=Report.FOUND).select_related('category', 'city')[:6]
    return render(request, 'core/home.html', {
        'latest_lost': latest_lost,
        'latest_found': latest_found,
    })
