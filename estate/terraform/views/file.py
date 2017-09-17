from __future__ import absolute_import
from django.apps import apps
from rest_framework import serializers, viewsets, filters
from estate.core.views import HistoricalSerializer, HistoryMixin, OwnsNamespace

Namespace = apps.get_model('terraform.Namespace')
File = apps.get_model('terraform.File')


######
# File
######
class FileSerializer(HistoricalSerializer):
    description = serializers.CharField(default="", allow_blank=True)
    namespace = serializers.SlugRelatedField(slug_field="slug", queryset=Namespace.objects.all())

    class Meta:
        model = File
        fields = ("pk", "slug", "title", "description", "namespace", "content", "disable", "created", "modified")
        historical_fields = ("pk", "slug", "title", "namespace", "description", "content", "disable")


class FileFilter(filters.FilterSet):

    class Meta:
        model = File
        fields = ["title", "namespace"]


class FileApiView(HistoryMixin, viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_class = FileFilter
    permission_classes = (OwnsNamespace, )
    filter_fields = ('slug',)
    search_fields = ('title',)
    ordering_fields = ('title', 'created', 'modified')
