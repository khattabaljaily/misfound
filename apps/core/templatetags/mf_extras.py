from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime as _naturaltime

register = template.Library()


@register.filter
def naturaltime_ar(value):
    """Same as humanize's naturaltime, but swaps the non-breaking space it
    inserts between a count and its unit (e.g. '28\xa0ثانية') for a normal
    space — the NBSP renders as a visible 'Â' glyph in Al-Mohanad."""
    return _naturaltime(value).replace('\xa0', ' ')
