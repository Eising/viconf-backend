from rest_framework import serializers
from configuration.models import (
    ResourceTemplate,
    ResourceService,
    Service,
    ServiceOrder,
)
from configuration.mustache import ViconfMustache


class ResourceTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True, required=False)
    platform = serializers.CharField(allow_null=True, required=False)
    up_contents = serializers.CharField()
    down_contents = serializers.CharField()
    fields = serializers.JSONField(read_only=True)
    labels = serializers.JSONField(read_only=True)
    deleted = serializers.BooleanField(default=False)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        up_template = ViconfMustache(template=validated_data['up_contents'])
        down_template = ViconfMustache(template=validated_data['down_contents'])
        tags = set()

        for tag in up_template.get_configurable_tags():
            tags.add(tag)
        for tag in down_template.get_configurable_tags():
            tags.add(tag)

        fields = {}
        labels = {}
        for tag in tags:
            fields[tag] = "none"
            labels[tag] = tag.capitalize()

        validated_data['fields'] = fields
        validated_data['labels'] = labels

        return ResourceTemplate.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        instance.platform = validated_data.get('platform', instance.platform)
        instance.up_contents = validated_data.get(
            'up_contents',
            instance.up_contents
        )
        instance.down_contents = validated_data.get(
            'down_contents',
            instance.down_contents
        )
        up_template = ViconfMustache(
            template=validated_data.get('up_contents', instance.up_contents)
        )
        down_template = ViconfMustache(
            template=validated_data.get('down_contents', instance.down_contents)
        )

        instance.deleted = validated_data.get('deleted', instance.deleted)
        tags = set()

        for tag in up_template.get_configurable_tags():
            tags.add(tag)
        for tag in down_template.get_configurable_tags():
            tags.add(tag)

        template_fields = sorted(set(instance.fields.keys()))

        if sorted(tags) != template_fields:
            for tag in tags:
                if tag not in template_fields:
                    instance.fields[tag] = "none"
                    instance.labels[tag] = tag.capitalize()

        # Remove old tags no longer in the template
        remove_tags = []
        for field in instance.fields.keys():
            if field not in tags:
                remove_tags.append(field)

        for tag in remove_tags:
            instance.fields.pop(tag)
            instance.labels.pop(tag)

        instance.save()

        return instance


class ResourceFieldsetSerializer(serializers.Serializer):
    name = serializers.CharField()
    validator = serializers.CharField()
    label = serializers.CharField()


class ResourceTagDefineSerializer(serializers.Serializer):
    resource_template_id = serializers.IntegerField(read_only=True)
    resource_fieldset = ResourceFieldsetSerializer(many=True)


class ResourceServiceSerializer(serializers.ModelSerializer):
    resource_templates = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ResourceTemplate.objects.all()
    )
    resource_template_list = ResourceTemplateSerializer(
        source="resource_templates",
        many=True,
        read_only=True
    )
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ResourceService
        fields = ['id', 'name', 'resource_templates', 'resource_template_list',
                  'node', 'defaults', 'created', 'modified']

    def create(self, validated_data):
        resource_templates = validated_data.pop('resource_templates', [])
        resource_service = ResourceService.objects.create(**validated_data)
        for template in resource_templates:
            resource_service.resource_templates.add(template)

        return resource_service


class ServiceSerializer(serializers.ModelSerializer):
    resource_services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ResourceService.objects.all()
    )
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'created', 'modified', 'resource_services']

    def create(self, validated_data):
        resource_services = validated_data.pop('resource_services', [])
        service = Service.objects.create(**validated_data)

        for resource in resource_services:
            service.resource_services.add(resource)

        return service


class ServiceOrderSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ServiceOrder
        fields = [
            'id',
            'reference',
            'customer',
            'location',
            'speed',
            'service',
            'template_fields',
            'created',
            'modified',
        ]


class ConfigurationSerializer(serializers.Serializer):
    node = serializers.CharField()
    service_up = serializers.CharField()
    service_down = serializers.CharField()
