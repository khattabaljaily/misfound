from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.locations.models import City, Country
from apps.reports.models import Category, Match, Report, ReportFlag
from .models import PageVisit

VISITS_CHART_DAYS = 30
ADMIN_VISITS_TOP_LIMIT = 8
ADMIN_VISITS_LOG_PAGE_SIZE = 30

ADMIN_FLAGS_PAGE_SIZE = 20


def _admin_context(active):
    return {'active': active, 'pending_flags_count': ReportFlag.objects.filter(resolved=False).count()}


def _country_flag(country_code):
    if not country_code or len(country_code) != 2:
        return ''
    return ''.join(chr(0x1F1E6 + ord(letter) - ord('A')) for letter in country_code.upper())


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /DDQ9RKHA/',
        'Disallow: /accounts/',
        'Disallow: /messages/',
        'Disallow: /notifications/',
        '',
        'Sitemap: ' + request.build_absolute_uri('/sitemap.xml'),
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def home(request):
    latest_lost = Report.objects.filter(status=Report.OPEN, type=Report.LOST).select_related('category', 'city')[:4]
    latest_found = Report.objects.filter(status=Report.OPEN, type=Report.FOUND).select_related('category', 'city')[:4]
    return render(request, 'core/home.html', {
        'latest_lost': latest_lost,
        'latest_found': latest_found,
        'categories': Category.objects.all(),
        'countries': Country.objects.all(),
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


@staff_member_required(login_url='accounts:login')
def admin_stats(request):
    total_reports = Report.objects.count()
    resolved_count = Report.objects.filter(status=Report.RESOLVED).count()
    resolved_rate = round(resolved_count / total_reports * 100) if total_reports else 0

    resolve_duration = ExpressionWrapper(F('updated_at') - F('created_at'), output_field=DurationField())
    avg_resolve = Report.objects.filter(status=Report.RESOLVED).annotate(
        duration=resolve_duration
    ).aggregate(avg=Avg('duration'))['avg']
    avg_resolve_days = round(avg_resolve.total_seconds() / 86400, 1) if avg_resolve else None

    top_categories = list(
        Category.objects.annotate(report_count=Count('reports'))
        .filter(report_count__gt=0).order_by('-report_count')[:6]
    )
    top_countries = list(
        Country.objects.annotate(report_count=Count('reports'))
        .filter(report_count__gt=0).order_by('-report_count')[:6]
    )

    context = {
        'total_reports': total_reports,
        'lost_count': Report.objects.filter(type=Report.LOST).count(),
        'found_count': Report.objects.filter(type=Report.FOUND).count(),
        'resolved_count': resolved_count,
        'resolved_rate': resolved_rate,
        'avg_resolve_days': avg_resolve_days,
        'total_matches': Match.objects.count(),
        'total_users': get_user_model().objects.count(),
        'top_categories': top_categories,
        'top_countries': top_countries,
        'max_category_count': top_categories[0].report_count if top_categories else 0,
        'max_country_count': top_countries[0].report_count if top_countries else 0,
        **_admin_context('dashboard'),
    }
    return render(request, 'core/admin_dashboard.html', context)


@staff_member_required(login_url='accounts:login')
def admin_visits(request):
    today = timezone.localdate()
    range_start = today - timedelta(days=VISITS_CHART_DAYS - 1)
    qs = PageVisit.objects.filter(created_at__date__gte=range_start)

    daily_rows = {
        row['day']: row for row in
        qs.annotate(day=TruncDate('created_at')).values('day')
        .annotate(visits=Count('id'), visitors=Count('visitor_id', distinct=True))
    }
    daily_series = []
    for offset in range(VISITS_CHART_DAYS):
        day = range_start + timedelta(days=offset)
        row = daily_rows.get(day)
        daily_series.append({'day': day, 'visits': row['visits'] if row else 0})
    max_daily_visits = max((d['visits'] for d in daily_series), default=0)

    top_pages = list(qs.values('path').annotate(visits=Count('id')).order_by('-visits')[:ADMIN_VISITS_TOP_LIMIT])
    top_referrers = list(
        qs.exclude(referer='').values('referer').annotate(visits=Count('id'))
        .order_by('-visits')[:ADMIN_VISITS_TOP_LIMIT]
    )

    top_countries = list(
        qs.exclude(country_code='').values('country_code').annotate(visits=Count('id'))
        .order_by('-visits')[:ADMIN_VISITS_TOP_LIMIT]
    )
    for row in top_countries:
        row['flag'] = _country_flag(row['country_code'])

    device_labels = dict(PageVisit.DEVICE_CHOICES)
    device_breakdown = list(
        qs.exclude(device_type='').values('device_type').annotate(visits=Count('id')).order_by('-visits')
    )
    for row in device_breakdown:
        row['label'] = device_labels.get(row['device_type'], row['device_type'])

    log_qs = PageVisit.objects.select_related('user').order_by('-created_at')
    page_obj = Paginator(log_qs, ADMIN_VISITS_LOG_PAGE_SIZE).get_page(request.GET.get('page'))
    for visit in page_obj:
        visit.country_flag = _country_flag(visit.country_code)

    context = {
        'visits_today': PageVisit.objects.filter(created_at__date=today).count(),
        'visitors_today': PageVisit.objects.filter(created_at__date=today)
            .values('visitor_id').distinct().count(),
        'visits_range': qs.count(),
        'visitors_range': qs.values('visitor_id').distinct().count(),
        'visits_all': PageVisit.objects.count(),
        'visitors_all': PageVisit.objects.values('visitor_id').distinct().count(),
        'chart_days': VISITS_CHART_DAYS,
        'daily_series': daily_series,
        'max_daily_visits': max_daily_visits,
        'top_pages': top_pages,
        'max_page_visits': top_pages[0]['visits'] if top_pages else 0,
        'top_referrers': top_referrers,
        'max_referrer_visits': top_referrers[0]['visits'] if top_referrers else 0,
        'top_countries': top_countries,
        'max_country_visits': top_countries[0]['visits'] if top_countries else 0,
        'device_breakdown': device_breakdown,
        'max_device_visits': device_breakdown[0]['visits'] if device_breakdown else 0,
        'visits_log': page_obj,
        'page_obj': page_obj,
        'base_qs': '',
        **_admin_context('visits'),
    }
    return render(request, 'core/admin_visits.html', context)


@staff_member_required(login_url='accounts:login')
def admin_flags(request):
    show_resolved = request.GET.get('resolved') == '1'
    qs = ReportFlag.objects.filter(resolved=show_resolved).select_related('report', 'reporter')
    page_obj = Paginator(qs, ADMIN_FLAGS_PAGE_SIZE).get_page(request.GET.get('page'))

    querystring = request.GET.copy()
    querystring.pop('page', None)

    context = {
        'flags': page_obj,
        'page_obj': page_obj,
        'base_qs': querystring.urlencode(),
        'show_resolved': show_resolved,
        **_admin_context('flags'),
    }
    return render(request, 'core/admin_flags.html', context)


@staff_member_required(login_url='accounts:login')
def admin_flag_resolve(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': _('طلب غير صالح.')}, status=405)
    flag = get_object_or_404(ReportFlag, pk=pk)
    flag.resolved = True
    flag.save(update_fields=['resolved'])
    return JsonResponse({'success': True, 'message': _('تم وسم البلاغ كمُراجَع.')})
