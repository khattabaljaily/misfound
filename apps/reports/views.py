from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.locations.models import City, Country
from .forms import ReportForm
from .models import Category, Report


def report_list(request):
    qs = Report.objects.filter(status=Report.OPEN).select_related('category', 'country', 'city')

    report_type = request.GET.get('type')
    if report_type in (Report.LOST, Report.FOUND):
        qs = qs.filter(type=report_type)

    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    country_id = request.GET.get('country')
    if country_id:
        qs = qs.filter(country_id=country_id)

    city_id = request.GET.get('city')
    if city_id:
        qs = qs.filter(city_id=city_id)

    q = request.GET.get('q')
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q)

    context = {
        'reports': qs[:100],
        'categories': Category.objects.all(),
        'countries': Country.objects.all(),
        'cities': City.objects.filter(country_id=country_id) if country_id else City.objects.none(),
        'selected': {
            'type': report_type or '',
            'category': category_id or '',
            'country': country_id or '',
            'city': city_id or '',
            'q': q or '',
        },
    }
    return render(request, 'reports/list.html', context)


def cities_for_country(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country_id=country_id).values('id', 'name_ar', 'name_en')
    return render(request, 'reports/_city_options.html', {'cities': cities})


def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related('category', 'country', 'city', 'reporter'), pk=pk
    )
    Report.objects.filter(pk=pk).update(views=F('views') + 1)
    is_owner = request.user.is_authenticated and request.user == report.reporter
    return render(request, 'reports/detail.html', {'report': report, 'is_owner': is_owner})


@login_required
def report_create(request, report_type):
    if report_type not in (Report.LOST, Report.FOUND):
        raise Http404

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, report_type=report_type)
        if form.is_valid():
            report = form.save(commit=False)
            report.type = report_type
            report.reporter = request.user
            report.save()
            messages.success(request, 'تم نشر البلاغ بنجاح.')
            return redirect('reports:detail', pk=report.pk)
    else:
        form = ReportForm(report_type=report_type)

    return render(request, 'reports/form.html', {'form': form, 'report_type': report_type})


@login_required
def my_reports(request):
    reports = Report.objects.filter(reporter=request.user).select_related('category')
    return render(request, 'reports/mine.html', {'reports': reports})


@login_required
def report_resolve(request, pk):
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    if request.method == 'POST':
        report.status = Report.RESOLVED
        report.save(update_fields=['status'])
        messages.success(request, 'تم وسم البلاغ كمسترجَع. الحمد لله على السلامة!')
    return redirect('reports:detail', pk=report.pk)
