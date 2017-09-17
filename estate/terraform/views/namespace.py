from __future__ import absolute_import
import django_filters
from django.apps import apps
from rest_framework import serializers, viewsets, filters, decorators, response
from estate.core.views import HistoricalSerializer, HistoryMixin, IsOwner
from .file import FileSerializer
from .template import TemplateInstanceSerializer
from ..terraform import Terraform

Namespace = apps.get_model('terraform.Namespace')
State = apps.get_model('terraform.State')


class NamespaceSerializer(HistoricalSerializer):
    description = serializers.CharField(default="", allow_blank=True)
    owner = serializers.SlugRelatedField(slug_field="name", read_only=True)
    files = FileSerializer(many=True, read_only=True, is_history=True)
    templates = TemplateInstanceSerializer(many=True, read_only=True, is_history=True)
    locking_user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    is_owner = serializers.SerializerMethodField(read_only=True)
    is_unlockable = serializers.SerializerMethodField(read_only=True)
    is_readonly = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Namespace
        fields = ("pk", "slug", "title", "description", "owner", "files", "templates", "locked", "locking_user", "is_owner", "is_unlockable", "is_readonly", "created", "modified")
        historical_fields = ("pk", "slug", "title", "description", "owner", "locked", "locking_user", "historical_files", "historical_templates")

    def get_is_owner(self, instance):
        if instance.owner:
            return self.context["request"].user.groups.filter(name=instance.owner).count() == 1
        else:
            return True

    def get_is_unlockable(self, instance):
        is_owner = self.get_is_owner(instance)
        return all([instance.is_unlockable(self.context["request"].user), is_owner])

    def get_is_readonly(self, instance):
        result = False
        if instance.locked is True:
            if instance.is_unlockable(self.context["request"].user) is not True:
                result = True
        return result


class NamespaceFilter(filters.FilterSet):
    owner = django_filters.CharFilter(label="owner", method="filter_is_owner")

    class Meta:
        model = Namespace
        fields = ["title", "owner", "slug"]

    def filter_is_owner(self, qs, name, value):
        return qs


class NamespaceApiView(HistoryMixin, viewsets.ModelViewSet):
    queryset = Namespace.objects.all()
    serializer_class = NamespaceSerializer
    filter_class = NamespaceFilter
    permission_classes = (IsOwner, )
    search_fields = ('title',)
    ordering_fields = ('title', 'created', 'modified')

    @decorators.detail_route(methods=["POST"])
    def lock(self, request, *args, **kwargs):

        if request.user.is_authenticated() is False:
            raise Exception("Unable to perform a lock for an anonymous user! {0}".format(request.user))
        instance = self.get_object()
        if instance.is_unlockable(request.user) is False:
            raise Exception("{0} is not lockable, it is currently locked by {1}".format(instance, instance.locking_user))
        instance.locked = True
        instance.locking_user = request.user
        instance.save()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.detail_route(methods=["POST"])
    def unlock(self, request, *args, **kwargs):
        if request.user.is_authenticated() is False:
            raise Exception("Unable to perform an unlock for an anonymous user!")
        instance = self.get_object()
        if instance.is_unlockable(request.user) is False:
            raise Exception("{0} is not unlockable, it is currently locked by {1}".format(instance, instance.locking_user))
        instance.locked = False
        instance.locking_user = None
        instance.save()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.detail_route(methods=["POST"])
    def plan(self, request, *args, **kwargs):
        instance = self.get_object()
        state_obj, _ = State.objects.get_or_create(namespace=instance, defaults={"title": instance.title, "namespace": instance})
        runner = Terraform("plan", instance, None, state_obj)
        runner.run()
        return response.Response(runner.get_stream())

    @decorators.detail_route(methods=["Get"])
    def plan_live(self, request, *args, **kwargs):
        instance = self.get_object()
        runner = Terraform("plan", instance, {})
        return response.Response(runner.get_stream())

    @decorators.detail_route(methods=["POST"], url_path=r'apply/(?P<plan_hash>.*)')
    def apply(self, request, plan_hash, *args, **kwargs):
        instance = self.get_object()
        state_obj, _ = State.objects.get_or_create(namespace=instance, defaults={"title": instance.title, "namespace": instance})
        runner = Terraform("apply", instance, plan_hash, state_obj)
        runner.run()
        return response.Response(runner.get_stream())

    @decorators.detail_route(methods=["Get"])
    def apply_live(self, request, *args, **kwargs):
        instance = self.get_object()
        runner = Terraform("apply", instance, {})
        return response.Response(runner.get_stream())

    @decorators.detail_route(methods=["POST"])
    def experiment(self, request, *args, **kwargs):
        instance = self.get_object()
        state_obj, _ = State.objects.get_or_create(namespace=instance, defaults={"title": instance.title, "namespace": instance})
        runner = Terraform("experiment", instance, None, state_obj, request.data["repl_command"])
        runner.run()
        return response.Response(runner.get_stream())

    @decorators.detail_route(methods=["Get"])
    def experiment_live(self, request, *args, **kwargs):
        instance = self.get_object()
        runner = Terraform("experiment", instance)
        return response.Response(runner.get_stream())
