from __future__ import absolute_import
from django.apps import apps
from rest_framework import serializers, viewsets, filters
from estate.core.views import HistoricalSerializer, HistoryMixin

Namespace = apps.get_model('terraform.Namespace')
State = apps.get_model('terraform.State')


class StateSerializer(HistoricalSerializer):
    description = serializers.CharField(default="", allow_blank=True)
    namespace = serializers.SlugRelatedField(slug_field="slug", queryset=Namespace.objects.all())

    class Meta:
        model = State
        fields = ("pk", "slug", "title", "description", "namespace", "content", "created", "modified")
        historical_fields = ("pk", "slug", "title", "namespace", "description", "content")


class StateFilter(filters.FilterSet):

    class Meta:
        model = State
        fields = ["title", "namespace"]


class StateApiView(HistoryMixin, viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_class = StateFilter
    filter_fields = ('slug',)
    search_fields = ('title',)
    ordering_fields = ('title', 'created', 'modified')
