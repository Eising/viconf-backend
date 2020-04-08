""" This view configures templates and services """
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import status

from .mixins import SafeDestroyModelMixin

from configuration.helpers import generate_service_schema

from configuration.validators import ViconfValidators, ViconfValidationError
from configuration.models import (
    ResourceTemplate,
    ResourceService,
    Service,
    ServiceOrder,
)
from configuration.serializers.resources import (
    ResourceTemplateSerializer,
    ResourceTagDefineSerializer,
    ResourceServiceSerializer,
    ServiceSerializer,
    ServiceOrderSerializer,
    ConfigurationSerializer
)

from configuration.mustache import (
    ViconfMustache,
)

# from configuration.validators import ViconfValidators, ViconfValidationError


class RetrieveUpdateSafeDestroyAPIView(
        SafeDestroyModelMixin, generics.RetrieveUpdateAPIView
):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ResourceTemplateList(generics.ListCreateAPIView):
    queryset = ResourceTemplate.objects.filter(deleted=False).all()
    serializer_class = ResourceTemplateSerializer
    permission_classes = [AllowAny]


class ResourceTemplateView(RetrieveUpdateSafeDestroyAPIView):
    queryset = ResourceTemplate.objects.filter(deleted=False).all()
    serializer_class = ResourceTemplateSerializer
    permission_classes = [AllowAny]


class ResourceTemplateFieldsetView(APIView):
    """ retrieve the set of tags or update them """
    permission_classes = [AllowAny]

    def get(self, request, pk, format=None):
        """
        Format the tags and send the serializer
        """
        template = get_object_or_404(ResourceTemplate, pk=pk)
        data = []
        for tag in template.fields.keys():
            data.append(
                {
                    "name": tag,
                    "validator": template.fields[tag],
                    "label": template.labels[tag]
                }
            )

        serializer = ResourceTagDefineSerializer({
            'resource_template_id': template.id,
            'resource_fieldset': data
        })

        return Response(serializer.data)

    def post(self, request, pk, format=None):
        serializer = ResourceTagDefineSerializer(data=request.data)
        if serializer.is_valid():
            template = get_object_or_404(
                ResourceTemplate,
                pk=pk
            )
            for field in request.data['resource_fieldset']:
                if field['name'] not in template.fields:
                    raise ValidationError(
                        f"{field['name']} not in template",
                        code=400
                    )
                template.labels[field['name']] = field['label']
                vival = ViconfValidators()
                if field['validator'] not in vival.VALIDATORS.keys():
                    raise ValidationError(
                        (f"{field['name']} has unknown validator "
                         f"{field['validator']}"),
                        code=400
                    )
                template.fields[field['name']] = field['validator']
                template.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class ResourceServiceList(generics.ListCreateAPIView):
    queryset = ResourceService.objects.all()
    serializer_class = ResourceServiceSerializer
    permission_classes = [AllowAny]


class ResourceServiceView(generics.RetrieveDestroyAPIView):
    # TODO: Maybe implement an Update function here
    queryset = ResourceService.objects.all()
    serializer_class = ResourceServiceSerializer
    permission_classes = [AllowAny]


class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]


class ServiceView(generics.RetrieveDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]


class ServiceOrderList(generics.ListCreateAPIView):
    queryset = ServiceOrder.objects.filter(deleted=False).all()
    serializer_class = ServiceOrderSerializer
    permission_classes = [AllowAny]


class ServiceOrderView(generics.RetrieveDestroyAPIView):
    queryset = ServiceOrder.objects.filter(deleted=False).all()
    serializer_class = ServiceOrderSerializer
    permission_classes = [AllowAny]


class ServiceConfigView(APIView):
    """ Fetch config for a service Order """
    permission_classes = [AllowAny]

    def get(self, request, pk, format=None):
        service_order = get_object_or_404(ServiceOrder, pk=pk)
        service_params = {
            "reference": service_order.reference,
            "customer": service_order.customer,
            "location": service_order.location,
            "service": service_order.service.name
        }

        service = service_order.service
        vival = ViconfValidators()

        config = {}
        for rs in service.resource_services.all():
            defaults = rs.defaults
            node = rs.node.hostname
            up_templates = []
            down_templates = []
            params = {}
            for template in rs.resource_templates.all():
                for field, validator in template.fields.items():
                    try:
                        params[field] = vival.test(
                            validator,
                            service_order.template_fields[node].get(
                                field,
                                next(
                                    (x['default'] for x in defaults
                                     if x['field'] == field),
                                    None
                                )
                            )
                        )
                    except ViconfValidationError:
                        raise ValidationError(
                            f"{field} is not a valid {validator}",
                            code=400
                        )

                up_templates.append(template.up_contents)
                down_templates.append(template.down_contents)

            if node not in config:
                config[node] = {"node": node}

            if "service_up" not in config[node]:
                config[node]["service_up"] = ""

            if "service_down" not in config[node]:
                config[node]["service_down"] = ""

            up_template = ViconfMustache(up_templates)
            down_template = ViconfMustache(down_templates)
            config[node]["service_up"] = up_template.compile(
                params=params,
                service_params=service_params
            )
            config[node]["service_down"] = down_template.compile(
                params=params,
                service_params=service_params

            )

        data = list(config.values())

        serializer = ConfigurationSerializer(data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceSchemaView(APIView):
    """ Retrieve a schema for a service that matches a ServiceOrder view"""
    permission_classes = [AllowAny]

    def get(self, request, pk, format=None):
        service = get_object_or_404(Service, pk=pk)
        schema = generate_service_schema(service)

        return Response(schema)
