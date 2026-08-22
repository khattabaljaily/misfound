from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ReportImage


@receiver(post_delete, sender=ReportImage)
def delete_report_image_file(sender, instance, **kwargs):
    """Remove the file from storage whenever a ReportImage row is deleted,
    including when it cascades from deleting the parent Report — Django
    never does this on its own."""
    if instance.image:
        instance.image.delete(save=False)
