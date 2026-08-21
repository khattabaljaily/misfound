from django.db.models import Avg, Count

from .models import Rating

TRUSTED_FINDER_MIN_RATINGS = 3
TRUSTED_FINDER_MIN_AVG = 4.5


def get_reputation(user):
    """Returns a user's aggregate rating stats and any badges they've earned."""
    agg = Rating.objects.filter(ratee=user).aggregate(avg=Avg('stars'), count=Count('id'))
    avg = round(agg['avg'], 1) if agg['avg'] else None
    count = agg['count']

    badges = []
    if count >= TRUSTED_FINDER_MIN_RATINGS and avg and avg >= TRUSTED_FINDER_MIN_AVG:
        badges.append('trusted')

    return {'avg': avg, 'count': count, 'badges': badges}
