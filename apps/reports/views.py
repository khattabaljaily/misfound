from datetime import timedelta
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import get_language, gettext as _

from apps.locations.models import City, Country
from .forms import ReportForm
from .matching import find_and_save_matches
from .models import Category, Match, Report, ReportFlag, ReportImage

REPORTS_PAGE_SIZE = 16
MINE_PAGE_SIZE = 12


def report_list(request):
    qs = Report.objects.filter(status=Report.OPEN).select_related('category', 'country', 'city').prefetch_related('images')

    report_type = request.GET.get('type')
    if report_type in (Report.LOST, Report.FOUND):
        qs = qs.filter(type=report_type)

    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Default the location filters to the user's own country/city so the feed
    # starts out relevant to them, but only when they haven't touched the
    # location filters themselves (the filter form always submits 'country',
    # even as an empty value, once the user has interacted with it).
    default_country_id = ''
    default_city_id = ''
    if 'country' not in request.GET and request.user.is_authenticated:
        if request.user.country_id:
            default_country_id = str(request.user.country_id)
        if request.user.city_id:
            default_city_id = str(request.user.city_id)

    country_id = request.GET.get('country', default_country_id)
    if country_id:
        qs = qs.filter(country_id=country_id)

    city_id = request.GET.get('city', default_city_id)
    if city_id:
        qs = qs.filter(city_id=city_id)

    q = request.GET.get('q')
    if q:
        qs = (
            qs.filter(title__icontains=q)
            | qs.filter(description__icontains=q)
            | qs.filter(identifier__icontains=q)
        )

    date_range = request.GET.get('date_range')
    if date_range in ('today', 'week', 'month'):
        since = {'today': 0, 'week': 7, 'month': 30}[date_range]
        qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=since))
    else:
        date_range = ''

    sort = request.GET.get('sort')
    if sort == 'oldest':
        qs = qs.order_by('created_at')
    elif sort == 'popular':
        qs = qs.order_by('-views')
    else:
        sort = 'newest'
        qs = qs.order_by('-created_at')

    map_rows = (
        qs.order_by()
        .exclude(city__isnull=True).exclude(city__lat__isnull=True)
        .values('city_id', 'city__lat', 'city__lng', 'city__name_ar', 'city__name_en')
        .annotate(
            lost_count=Count('id', filter=Q(type=Report.LOST)),
            found_count=Count('id', filter=Q(type=Report.FOUND)),
        )
    )
    map_points = [
        {
            'id': row['city_id'],
            'name': row['city__name_ar'] if get_language() == 'ar' else row['city__name_en'],
            'lat': row['city__lat'],
            'lng': row['city__lng'],
            'lost': row['lost_count'],
            'found': row['found_count'],
            'url': f"{request.path}?city={row['city_id']}",
        }
        for row in map_rows
    ]

    paginator = Paginator(qs, REPORTS_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    querystring = request.GET.copy()
    querystring.pop('page', None)

    if report_type == Report.LOST:
        meta_title = _('المفقودات') + ' | Misfound'
        meta_description = _('تصفح أحدث إعلانات المفقودات في الوطن العربي وساعد في إعادتها إلى أصحابها.')
    elif report_type == Report.FOUND:
        meta_title = _('المعثورات') + ' | Misfound'
        meta_description = _('تصفح أحدث إعلانات المعثورات في الوطن العربي وساعد في إيصالها إلى أصحابها.')
    else:
        meta_title = _('تصفح الإعلانات') + ' | Misfound'
        meta_description = _('تصفح جميع إعلانات المفقودات والمعثورات في الوطن العربي في مكان واحد.')

    context = {
        'reports': page_obj,
        'page_obj': page_obj,
        'map_points': map_points,
        'base_qs': querystring.urlencode(),
        'meta_title': meta_title,
        'meta_description': meta_description,
        'categories': Category.objects.all(),
        'countries': Country.objects.all(),
        'cities': City.objects.filter(country_id=country_id) if country_id else City.objects.none(),
        'selected': {
            'type': report_type or '',
            'category': category_id or '',
            'country': country_id or '',
            'city': city_id or '',
            'q': q or '',
            'date_range': date_range or '',
            'sort': sort,
        },
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'reports/_results.html', context)
    return render(request, 'reports/list.html', context)


def cities_for_country(request):
    country_id = request.GET.get('country')
    order_field = 'name_ar' if get_language() == 'ar' else 'name_en'
    cities = City.objects.filter(country_id=country_id).order_by(order_field)
    return JsonResponse([{'id': c.id, 'name': c.name} for c in cities], safe=False)


def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related('category', 'country', 'city', 'reporter')
        .prefetch_related('images'),
        pk=pk,
    )
    Report.objects.filter(pk=pk).update(views=F('views') + 1)
    is_owner = request.user.is_authenticated and request.user == report.reporter

    if report.type == Report.LOST:
        matches = Match.objects.filter(lost_report=report).select_related(
            'found_report', 'found_report__category', 'found_report__city'
        ).prefetch_related('found_report__images')
        matched_reports = [(m.found_report, m.score, m.reason) for m in matches]
    else:
        matches = Match.objects.filter(found_report=report).select_related(
            'lost_report', 'lost_report__category', 'lost_report__city'
        ).prefetch_related('lost_report__images')
        matched_reports = [(m.lost_report, m.score, m.reason) for m in matches]

    already_flagged = (
        request.user.is_authenticated
        and ReportFlag.objects.filter(report=report, reporter=request.user).exists()
    )

    absolute_url = request.build_absolute_uri(report.get_absolute_url())
    share_text = f'{report.get_type_display()}: {report.title}\n{absolute_url}'

    location_bit = report.city.name if report.city else report.country.name
    meta_description = (
        f'{report.get_type_display()} · {report.category.name} · {location_bit} — '
        + Truncator(report.description).chars(120)
    )

    return render(request, 'reports/detail.html', {
        'report': report, 'is_owner': is_owner, 'matched_reports': matched_reports,
        'already_flagged': already_flagged,
        'absolute_url': absolute_url,
        'whatsapp_share_url': 'https://wa.me/?text=' + quote(share_text),
        'meta_title': f'{report.title} | Misfound',
        'meta_description': meta_description,
        'meta_image': request.build_absolute_uri(report.cover_image.image.url) if report.cover_image else None,
        'canonical_url': absolute_url,
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
            for i, f in enumerate(form.cleaned_data['images']):
                ReportImage.objects.create(report=report, image=f, order=i)
            find_and_save_matches(report)
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': report.get_absolute_url()})
            messages.success(request, _('تم نشر الإعلان بنجاح.'))
            return redirect('reports:detail', pk=report.pk)

        if is_ajax:
            return render(
                request, 'reports/_form.html', {'form': form, 'report_type': report_type}, status=400
            )
    else:
        form = ReportForm(report_type=report_type)

    return render(request, 'reports/form.html', {'form': form, 'report_type': report_type})


@login_required
def report_edit(request, pk):
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report, report_type=report.type)
        if form.is_valid():
            form.save()
            next_order = report.images.count()
            for i, f in enumerate(form.cleaned_data['images']):
                ReportImage.objects.create(report=report, image=f, order=next_order + i)
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': report.get_absolute_url()})
            messages.success(request, _('تم تحديث الإعلان بنجاح.'))
            return redirect('reports:detail', pk=report.pk)

        if is_ajax:
            return render(
                request, 'reports/_form.html',
                {'form': form, 'report_type': report.type, 'report': report}, status=400
            )
    else:
        form = ReportForm(instance=report, report_type=report.type)

    return render(request, 'reports/form.html', {'form': form, 'report_type': report.type, 'report': report})


@login_required
def report_image_delete(request, pk):
    image = get_object_or_404(ReportImage, pk=pk, report__reporter=request.user)

    if request.method != 'POST':
        raise Http404

    image.delete()
    return JsonResponse({'success': True})


@login_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method != 'POST':
        raise Http404

    report.delete()
    if is_ajax:
        return JsonResponse({'success': True, 'redirect': reverse('reports:mine')})
    messages.success(request, _('تم حذف الإعلان بنجاح.'))
    return redirect('reports:mine')


@login_required
def my_reports(request):
    qs = Report.objects.filter(reporter=request.user).select_related('category', 'city').prefetch_related('images')
    page_obj = Paginator(qs, MINE_PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'reports/mine.html', {'reports': page_obj, 'page_obj': page_obj})


@login_required
def flag_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method != 'POST':
        raise Http404

    if report.reporter == request.user:
        if is_ajax:
            return JsonResponse({'success': False, 'message': _('لا يمكنك الإبلاغ عن إعلانك الخاص.')}, status=400)
        raise Http404

    reason = request.POST.get('reason')
    if reason not in dict(ReportFlag.REASON_CHOICES):
        if is_ajax:
            return JsonResponse({'success': False, 'message': _('يرجى اختيار سبب الإبلاغ.')}, status=400)
        raise Http404

    existing_flag, created = ReportFlag.objects.get_or_create(
        report=report, reporter=request.user,
        defaults={'reason': reason, 'note': request.POST.get('note', '')[:300]},
    )
    message = _('تم استلام بلاغك، شكرًا لمساعدتك في الحفاظ على جودة المنصة.') if created else _('سبق أن أبلغت عن هذا الإعلان.')
    if is_ajax:
        return JsonResponse({'success': True, 'message': message})
    messages.success(request, message)
    return redirect('reports:detail', pk=pk)


@login_required
def report_resolve(request, pk):
    report = get_object_or_404(Report, pk=pk, reporter=request.user)
    if request.method == 'POST':
        report.status = Report.RESOLVED
        report.save(update_fields=['status'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': _('تم تحديث حالة الإعلان إلى «تم الاسترجاع» بنجاح.')})
        messages.success(request, _('تم تحديث حالة الإعلان إلى «تم الاسترجاع» بنجاح.'))
    return redirect('reports:detail', pk=report.pk)
