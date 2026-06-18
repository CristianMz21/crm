"""Signal handlers for pipeline app models.

Enforces that exactly one Pipeline has ``es_default=True`` at any
time.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from pipeline.models import Pipeline


@receiver(pre_save, sender=Pipeline)
def ensure_single_default_pipeline(sender, instance, **kwargs):
    """If this pipeline is being set as default, unset all others."""
    if instance.es_default:
        Pipeline.objects.filter(es_default=True).exclude(pk=instance.pk).update(es_default=False)
