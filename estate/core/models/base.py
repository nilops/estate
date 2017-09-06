from __future__ import absolute_import
import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from django_permanent.models import PermanentModel
from simple_history.models import HistoricalRecords
from rest_framework.authtoken.models import Token
from .fields import SoftDeleteAwareAutoSlugField

LOG = logging.getLogger(__name__)


class HistoricalRecordsWithoutDelete(HistoricalRecords):
    def post_delete(self, *args, **kwargs):
        # Fixes issue
        # https://github.com/treyhunner/django-simple-history/issues/207
        pass


class EstateAbstractBase(PermanentModel, TimeStampedModel, TitleDescriptionModel):
    slug = SoftDeleteAwareAutoSlugField(_('slug'), populate_from='title')

    class Meta(TimeStampedModel.Meta):
        abstract = True

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return "<%s:%s pk:%i>" % (self.__class__.__name__, self.title, self.pk)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
