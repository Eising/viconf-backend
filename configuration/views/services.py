""" This view configures templates and services """
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import status

from .mixins import SafeDestroyModelMixin

from configuration.helpers import generate_service_schema

from configuration.validators import ViconfValidators, ViconfValidationError
from configuration.models import (
    Node,
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ResourceTemplateView(RetrieveUpdateSafeDestroyAPIView):
    queryset = ResourceTemplate.objects.filter(deleted=False).all()
    serializer_class = ResourceTemplateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def update_related_rs(self, instance):
        template = instance
        template_fields = list(template.fields.keys())
        related = ResourceService.objects.filter(resource_templates__id=instance.id)
        for rs in related:
            defaults = [field for field in rs.defaults if field['field'] in template_fields]
            default_fields = [field['field'] for field in defaults]
            new_fields = [field for field in template_fields if field not in default_fields]
            for field in new_fields:
                defaults.append(
                    {
                        "field": field,
                        "configurable": True,
                        "default": None
                    }
                )

            rs.defaults = defaults
            rs.save()

    def perform_update(self, serializer):

        instance = serializer.instance
        serializer.save()
        self.update_related_rs(instance)



class ResourceTemplateFieldsetView(APIView):
    """ retrieve the set of tags or update them """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ResourceServiceView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResourceService.objects.all()
    serializer_class = ResourceServiceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ServiceView(generics.RetrieveDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ServiceOrderList(generics.ListCreateAPIView):
    queryset = ServiceOrder.objects.filter(deleted=False).all()
    serializer_class = ServiceOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ServiceOrderView(generics.RetrieveDestroyAPIView):
    queryset = ServiceOrder.objects.filter(deleted=False).all()
    serializer_class = ServiceOrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class ServiceConfigView(APIView):
    """ Fetch config for a service Order """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
            if rs.node is None:
                # The rs doesn't enforce node, so we pick the first node
                nodeobj = Node.objects.get(
                    hostname=list(
                        service_order.template_fields.keys()
                    )[0]
                )
                node = nodeobj.hostname
            else:
                nodeobj = rs.node
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

            params["node"] = node
            params["node_ipv4"] = nodeobj.ipv4
            params["node_ipv6"] = nodeobj.ipv6

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk, format=None):
        service = get_object_or_404(Service, pk=pk)
        schema = generate_service_schema(service)

        return Response(schema)
