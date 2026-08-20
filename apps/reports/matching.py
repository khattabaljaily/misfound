import json
import logging

import requests
from django.conf import settings
from django.db import IntegrityError

from apps.notifications.services import notify

from .models import Match, Report

logger = logging.getLogger(__name__)

CANDIDATE_LIMIT = 15
SCORE_THRESHOLD = 40
DATE_WINDOW_DAYS = 60


def _candidates_for(report):
    """Open reports of the opposite type, same category & country, ranked
    by how close their event_date is to this report's."""
    opposite_type = Report.FOUND if report.type == Report.LOST else Report.LOST
    qs = Report.objects.filter(
        type=opposite_type, status=Report.OPEN,
        category=report.category, country=report.country,
    ).exclude(pk=report.pk).select_related('city')

    candidates = list(qs[:80])
    candidates.sort(key=lambda c: abs((c.event_date - report.event_date).days))
    return candidates[:CANDIDATE_LIMIT]


def _build_prompt(report, candidates):
    kind = 'مفقود' if report.type == Report.LOST else 'تم العثور عليه'
    opposite_kind = 'معثور عليها' if report.type == Report.LOST else 'مفقودة'

    target = (
        f"العنوان: {report.title}\n"
        f"الوصف: {report.description}\n"
        f"التصنيف: {report.category.name_ar}\n"
        f"المدينة: {report.city.name_ar if report.city else 'غير محددة'}\n"
        f"التاريخ: {report.event_date}"
    )

    lines = []
    for c in candidates:
        lines.append(
            f"- id={c.id} | العنوان: {c.title} | الوصف: {c.description} | "
            f"المدينة: {c.city.name_ar if c.city else 'غير محددة'} | التاريخ: {c.event_date}"
        )
    candidates_block = '\n'.join(lines)

    return (
        f"هذا إعلان عن غرض {kind}:\n{target}\n\n"
        f"وهذه إعلانات {opposite_kind} مرشحة لنفس التصنيف والدولة:\n{candidates_block}\n\n"
        "قيّم مدى احتمال أن كل مرشح يصف نفس الغرض بالإعلان الأول، بناءً على الوصف والمكان "
        "والتاريخ فقط. أعطِ نسبة من 0 إلى 100 لكل مرشح، وسببًا مختصرًا بالعربية لا يتجاوز "
        "١٥ كلمة. اذكر فقط المرشحين الذين نسبتهم ٤٠ أو أكثر. أجب بصيغة JSON فقط بالشكل التالي:\n"
        '{"matches": [{"id": 12, "score": 75, "reason": "..."}]}'
    )


def _call_deepseek(prompt):
    if not settings.DEEPSEEK_API_KEY:
        return None
    try:
        response = requests.post(
            settings.DEEPSEEK_API_URL,
            headers={
                'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': settings.DEEPSEEK_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': (
                            'أنت مساعد يقارن بين إعلانات المفقودات والمعثورات في منصة Misfound '
                            'ويحدد مدى احتمال تطابقها. أجب بصيغة JSON فقط، بدون أي نص إضافي.'
                        ),
                    },
                    {'role': 'user', 'content': prompt},
                ],
                'temperature': 0.2,
                'response_format': {'type': 'json_object'},
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception:
        logger.exception('DeepSeek matching request failed')
        return None


def find_and_save_matches(report):
    """Finds AI-suggested matches for `report` among open opposite-type
    reports and saves them. Returns the list of new Match objects created."""
    candidates = _candidates_for(report)
    if not candidates:
        return []

    data = _call_deepseek(_build_prompt(report, candidates))
    if not data or not isinstance(data.get('matches'), list):
        return []

    candidates_by_id = {c.id: c for c in candidates}
    created = []

    for entry in data['matches']:
        try:
            candidate_id = int(entry.get('id'))
            score = int(entry.get('score'))
        except (TypeError, ValueError):
            continue

        candidate = candidates_by_id.get(candidate_id)
        if not candidate or score < SCORE_THRESHOLD:
            continue

        lost_report, found_report = (
            (report, candidate) if report.type == Report.LOST else (candidate, report)
        )
        try:
            match, is_new = Match.objects.update_or_create(
                lost_report=lost_report, found_report=found_report,
                defaults={'score': min(score, 100), 'reason': str(entry.get('reason', ''))[:300]},
            )
            created.append(match)
        except IntegrityError:
            continue

        if is_new and lost_report.reporter_id != found_report.reporter_id:
            level = 'تطابق قوي' if match.score >= 70 else 'تطابق محتمل'
            notify(
                lost_report.reporter, 'match',
                f'{level} ({match.score}%) لإعلانك: {lost_report.title}',
                found_report.title, lost_report.get_absolute_url(),
            )
            notify(
                found_report.reporter, 'match',
                f'{level} ({match.score}%) لإعلانك: {found_report.title}',
                lost_report.title, found_report.get_absolute_url(),
            )

    return created
