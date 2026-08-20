from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime as _naturaltime

register = template.Library()


@register.filter
def naturaltime_ar(value):
    """Same as humanize's naturaltime, but swaps the non-breaking space it
    inserts between a count and its unit (e.g. '28\xa0ثانية') for a normal
    space — the NBSP renders as a visible 'Â' glyph in Al-Mohanad."""
    return _naturaltime(value).replace('\xa0', ' ')


@register.filter
def page_range(page_obj, window=2):
    """Page numbers to render for `page_obj`, with None marking an elided gap."""
    total = page_obj.paginator.num_pages
    current = page_obj.number
    pages = []
    for num in range(1, total + 1):
        if num == 1 or num == total or current - window <= num <= current + window:
            pages.append(num)
        elif pages and pages[-1] is not None:
            pages.append(None)
    return pages
