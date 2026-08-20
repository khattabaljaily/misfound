from django.contrib import admin
from django.http import Http404

admin.site.site_header = 'إدارة موقع Misfound'
admin.site.site_title = 'إدارة Misfound'
admin.site.index_title = 'لوحة التحكم'


def _disabled_admin_login(request, extra_context=None):
    """Disables the self-service login form at /admin/login/. Staff must
    authenticate through the site's own login page; already-authenticated
    staff/superusers reach the admin normally (this only blocks the
    anonymous-visitor login prompt)."""
    raise Http404


admin.site.login = _disabled_admin_login
