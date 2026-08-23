import uuid

from geoip2fast import GeoIP2Fast
from user_agents import parse as parse_user_agent

from .models import PageVisit

VISITOR_COOKIE_NAME = 'mf_vid'
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365
EXCLUDED_PATH_PREFIXES = ('DDQ9RKHA/', 'admin/')

_geoip = GeoIP2Fast()


class VisitorTrackingMiddleware:
    """Logs a PageVisit for real, anonymous-facing HTML page loads.

    Restricting to GET + text/html responses keeps JSON polling endpoints
    (e.g. notifications/unread-count/, hit every 45s by the navbar) out of
    the visit counts without having to hardcode every such endpoint here.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._track(request, response)
        return response

    def _track(self, request, response):
        if request.method != 'GET' or response.status_code != 200:
            return
        if not response.get('Content-Type', '').startswith('text/html'):
            return
        if request.path.lstrip('/').startswith(EXCLUDED_PATH_PREFIXES):
            return
        if request.user.is_authenticated and request.user.is_staff:
            return

        visitor_id = request.COOKIES.get(VISITOR_COOKIE_NAME)
        is_new_visitor = not visitor_id
        if is_new_visitor:
            visitor_id = uuid.uuid4().hex

        ip_address = self._client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

        PageVisit.objects.create(
            path=request.path[:255],
            visitor_id=visitor_id,
            ip_address=ip_address,
            country_code=self._country_code(ip_address),
            user=request.user if request.user.is_authenticated else None,
            referer=request.META.get('HTTP_REFERER', '')[:255],
            user_agent=user_agent,
            device_type=self._device_type(user_agent),
        )

        if is_new_visitor:
            response.set_cookie(
                VISITOR_COOKIE_NAME, visitor_id,
                max_age=VISITOR_COOKIE_MAX_AGE, httponly=True, samesite='Lax',
            )

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def _country_code(ip_address):
        if not ip_address:
            return ''
        result = _geoip.lookup(ip_address)
        if not result or result.is_private or len(result.country_code) != 2:
            return ''
        return result.country_code

    @staticmethod
    def _device_type(user_agent):
        if not user_agent:
            return ''
        ua = parse_user_agent(user_agent)
        if ua.is_mobile:
            return PageVisit.MOBILE
        if ua.is_tablet:
            return PageVisit.TABLET
        if ua.is_pc:
            return PageVisit.DESKTOP
        return PageVisit.OTHER
