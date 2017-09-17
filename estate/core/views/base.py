from __future__ import absolute_import
from django.db.models.query import QuerySet
from rest_framework import serializers, decorators, response, permissions


class HistoricalSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        is_history = kwargs.pop("is_history", False)
        super(HistoricalSerializer, self).__init__(*args, **kwargs)
        if is_history:
            instance = self.instance
            if isinstance(instance, QuerySet):
                try:
                    instance = instance[0]
                except IndexError:
                    instance = None
            if all([hasattr(instance, "history_id"), hasattr(instance, "history_user"), hasattr(instance, "history_date")]):
                self.fields['user'] = serializers.SlugRelatedField(source="history_user", slug_field="username", read_only=True)
                self.fields['date'] = serializers.DateTimeField(source="history_date", read_only=True)
                allowed = set(getattr(self.Meta, "historical_fields", tuple()) + ('user', 'date'))
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class HistoryMixin(object):

    @decorators.detail_route(methods=["GET"])
    def history(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance.history.all(), many=True, is_history=True)
        return response.Response(serializer.data)


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner:
            return request.user.groups.filter(name=obj.owner).count() == 1
        else:
            return True


class OwnsNamespace(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.namespace.owner:
            return request.user.groups.filter(name=obj.namespace.owner).count() == 1
        else:
            return True
