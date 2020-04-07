from configuration.models import Service, ResourceService, ResourceTemplate
import re


def generate_service_schema(service):

    template_fields = {}
    for rs in service.resource_services.all():
        if rs.node is not None:
            key = rs.node.hostname
        else:
            key = "__NONODE__"

        if key not in template_fields:
            template_fields[key] = {}

        for template in rs.resource_templates.all():
            for field, validator in template.fields.items():
                if field not in template_fields[key]:
                    defaults = next((x for x in rs.defaults if x['field'] == field), None)
                    if defaults is not None:
                        default_val = defaults['default']
                        configurable = defaults['configurable']
                    else:
                        default_val = None,
                        configurable = True

                    if configurable:
                        template_fields[key][field] = {
                            'label': template.labels[field],
                            'validator': validator,
                            'default': default_val
                        }

    schema = {
        "reference": None,
        "customer": None,
        "location": None,
        "speed": None,
        "service": service.id,
        "template_fields": template_fields

    }

    return schema
