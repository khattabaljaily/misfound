from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.shortcuts import render

from apps.locations.models import City, Country
from apps.reports.models import Category, Match, Report, ReportFlag


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


@staff_member_required
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
        'pending_flags': ReportFlag.objects.filter(resolved=False).count(),
        'top_categories': top_categories,
        'top_countries': top_countries,
        'max_category_count': top_categories[0].report_count if top_categories else 0,
        'max_country_count': top_countries[0].report_count if top_countries else 0,
    }
    return render(request, 'core/admin_stats.html', context)
