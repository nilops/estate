import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ...core.models.base import EstateAbstractBase, HistoricalRecordsWithoutDelete

LOG = logging.getLogger(__name__)


class State(EstateAbstractBase):
    content = models.TextField(_("content"), blank=True)
    namespace = models.ForeignKey("terraform.Namespace", related_name="state")

    history = HistoricalRecordsWithoutDelete(excluded_fields=['slug'])
