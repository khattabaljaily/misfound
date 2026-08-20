from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.locations.models import City, Country
from .forms import ReportForm
from .matching import find_and_save_matches
from .models import Category, Match, Report


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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'reports/_results.html', context)
    return render(request, 'reports/list.html', context)


def cities_for_country(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country_id=country_id).order_by('name_ar').values('id', 'name_ar')
    return JsonResponse(list(cities), safe=False)


def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related('category', 'country', 'city', 'reporter'), pk=pk
    )
    Report.objects.filter(pk=pk).update(views=F('views') + 1)
    is_owner = request.user.is_authenticated and request.user == report.reporter

    if report.type == Report.LOST:
        matches = Match.objects.filter(lost_report=report).select_related(
            'found_report', 'found_report__category', 'found_report__city'
        )
        matched_reports = [(m.found_report, m.score, m.reason) for m in matches]
    else:
        matches = Match.objects.filter(found_report=report).select_related(
            'lost_report', 'lost_report__category', 'lost_report__city'
        )
        matched_reports = [(m.lost_report, m.score, m.reason) for m in matches]

    return render(request, 'reports/detail.html', {
        'report': report, 'is_owner': is_owner, 'matched_reports': matched_reports,
    })


@login_required
def report_create(request, report_type):
    if report_type not in (Report.LOST, Report.FOUND):
        raise Http404

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, report_type=report_type)
        if form.is_valid():
            report = form.save(commit=False)
            report.type = report_type
            report.reporter = request.user
            report.save()
            find_and_save_matches(report)
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': report.get_absolute_url()})
            messages.success(request, 'تم نشر الإعلان بنجاح.')
            return redirect('reports:detail', pk=report.pk)

        if is_ajax:
            return render(
                request, 'reports/_form.html', {'form': form, 'report_type': report_type}, status=400
            )
    else:
        form = ReportForm(report_type=report_type)

    return render(request, 'reports/form.html', {'form': form, 'report_type': report_type})


@login_required
def my_reports(request):
    reports = Report.objects.filter(reporter=request.user).select_related('category', 'city')
    return render(request, 'reports/mine.html', {'reports': reports})


@login_required
def report_resolve(request, pk):
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    if request.method == 'POST':
        report.status = Report.RESOLVED
        report.save(update_fields=['status'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'تم تحديث حالة الإعلان إلى «تم الاسترجاع» بنجاح.'})
        messages.success(request, 'تم تحديث حالة الإعلان إلى «تم الاسترجاع» بنجاح.')
    return redirect('reports:detail', pk=report.pk)
