import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend

logger = logging.getLogger(__name__)


class RotatingSMTPEmailBackend(SMTPEmailBackend):
    """
    SMTP backend that spreads outgoing mail across the mailboxes listed in
    settings.EMAIL_ACCOUNTS instead of always sending through one, so a
    single mailbox's hourly sending cap (settings.EMAIL_HOURLY_LIMIT) isn't
    hit while the others sit unused.

    Each message is authenticated and sent as whichever configured mailbox
    has sent the fewest emails in the current clock hour, so the From
    address rotates along with the SMTP login.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent = 0
        for message in email_messages:
            account = self._pick_account()
            self.username = account['user']
            self.password = account['password']
            message.from_email = f'Misfound <{account["user"]}>'
            self.connection = None
            if super().send_messages([message]):
                self._record_send(account['user'])
                sent += 1
        return sent

    def _pick_account(self):
        accounts = settings.EMAIL_ACCOUNTS
        counts = {a['user']: cache.get(self._bucket_key(a['user']), 0) for a in accounts}
        account = min(accounts, key=lambda a: counts[a['user']])
        if counts[account['user']] >= settings.EMAIL_HOURLY_LIMIT:
            logger.warning(
                'All Misfound mailboxes are at or above their hourly send limit (%s/hour).',
                settings.EMAIL_HOURLY_LIMIT,
            )
        return account

    def _record_send(self, user):
        key = self._bucket_key(user)
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=3600)

    @staticmethod
    def _bucket_key(user):
        return f'email_quota:{user}:{time.strftime("%Y%m%d%H")}'
