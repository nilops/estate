from __future__ import absolute_import
import logging
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_permanent.signals import post_restore
from ...core.models.base import EstateAbstractBase, HistoricalRecordsWithoutDelete
from .template import TemplateInstance
from .file import File
from .state import State

LOG = logging.getLogger(__name__)


class Namespace(EstateAbstractBase):
    owner = models.ForeignKey("auth.Group", related_name="namespaces", null=True, blank=True)
    locked = models.BooleanField(_('locked'), default=False)
    locking_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="locked_namespaces", null=True, blank=True)
    # TODO: Add tags

    history = HistoricalRecordsWithoutDelete(excluded_fields=['slug'])

    def is_unlockable(self, user):
        if self.locked is True:
            if self.locking_user == user:
                return True
            else:
                return False
        return True

    @property
    def terraform_files(self):
        output = []
        output += [f for f in self.files.all() if f.disable is False]
        output += [t for t in self.templates.all() if t.disable is False]
        return output


@receiver(post_restore, sender=Namespace)
def restore_related_objects(sender, instance, *args, **kwargs):
    LOG.info("Restoring {0} Related Objects".format(instance))
    for F in File.deleted_objects.filter(namespace__id=instance.pk):
        F.restore()
    for T in TemplateInstance.deleted_objects.filter(namespace__id=instance.pk):
        T.restore()
    for S in State.deleted_objects.filter(namespace__id=instance.pk):
        S.restore()
