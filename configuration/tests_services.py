from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from configuration.models import (
    ResourceTemplate,
    ResourceService,
    Node,
    Service
)
from django.contrib.auth.models import User


class ServiceTests(APITestCase):
    fixtures = ['nodeandtemplate', 'user']

    def test_fixture(self):
        self.assertEqual(ResourceTemplate.objects.count(), 1)

    def test_create_rs(self):

        data = {
            "name": "Test",
            "node": Node.objects.get().hostname,
            "defaults": {
                "place": "World",
                "day": "Wednesday"
            },
            "resource_templates": [
                ResourceTemplate.objects.get().id
            ]
        }
        url = reverse("configuration:resource_service_list")
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceService.objects.count(), 1)
        self.assertEqual(
            ResourceService.objects.get().resource_templates.count(),
            1
        )
        self.assertEqual(
            ResourceService.objects.get().defaults['place'],
            'World'
        )

    def test_create_service(self):
        rs = ResourceService.objects.create(
            name="Test",
            node=Node.objects.get(),
            defaults=[
                {
                    "field": "place",
                    "default": "World",
                    "configurable": False
                },
                {
                    "field": "day",
                    "default": "Wednesday",
                    "configurable": True
                }
            ]
        )

        rs.resource_templates.add(ResourceTemplate.objects.get())

        data = {
            "name": "A service",
            "resource_services": [
                rs.id
            ]
        }

        url = reverse("configuration:service_list")
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.get().resource_services.count(), 1)
        self.assertEqual(Service.objects.get().name, "A service")

    def test_service_order(self):
        rs = ResourceService.objects.create(
            node=Node.objects.get(),
            defaults=[
                {
                    "field": "place",
                    "default": "World",
                    "configurable": False
                },
                {
                    "field": "day",
                    "default": "Wednesday",
                    "configurable": True
                }
            ]
        )

        rs.resource_templates.add(ResourceTemplate.objects.get())

        ser = Service.objects.create(name="A service")
        ser.resource_services.add(rs)

        data = {
            "reference": "TEST-1",
            "service": ser.id,
            "template_fields": {
                Node.objects.get().hostname: {
                    "day": "Thursday",
                    "place": "Norway"
                }
            }
        }

        url = reverse("configuration:service_order_list")
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        id = response.data['id']

        config_url = reverse(
            "configuration:service_config_view", kwargs={"pk": id}
        )

        config_response = self.client.get(config_url, format='json')
        self.assertEqual(config_response.data[0]['node'], 'test.node')

    def test_service_schema(self):
        rs1 = ResourceService.objects.create(
            node=Node.objects.get(),
            defaults=[
                {
                    "field": "place",
                    "default": "World",
                    "configurable": False
                },
                {
                    "field": "day",
                    "default": "Wednesday",
                    "configurable": True
                }
            ]
        )
        rs2 = ResourceService.objects.create(
            node=None,
            defaults=[
                {
                    "field": "place",
                    "default": "Venus",
                    "configurable": False
                },
                {
                    "field": "day",
                    "default": "Thursday",
                    "configurable": True
                }
            ]
        )
        rs1.resource_templates.add(ResourceTemplate.objects.get())
        rs2.resource_templates.add(ResourceTemplate.objects.get())

        ser = Service.objects.create(name="A service")
        ser.resource_services.add(rs1)
        ser.resource_services.add(rs2)

        url = reverse(
            'configuration:service_schema_view', kwargs={"pk": ser.id}
        )

        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('__NONODE__', response.data['template_fields'])
        self.assertIn(
            Node.objects.get().hostname, response.data['template_fields']
        )

    def test_subtemplates(self):
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        template1 = """{{! maintemplate }}
Further content:
{{! subtemplates }}
Nothing more here.
"""
        template2 = "template2: {{ var1 }}"
        template3 = "template3: {{ var1 }} {{ var2 }}"

        templates = [template1, template2, template3]
        for template in templates:
            data = {
                "name": "mtemplate",
                "up_contents": template,
                "down_contents": "nothing"
            }

            url = reverse("configuration:resource_template_list")
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rs = ResourceService.objects.create(
            name="Test",
            node=Node.objects.get(),
            defaults=[
                {
                    "field": "var1",
                    "default": "Hello",
                    "configurable": False
                },
                {
                    "field": "var2",
                    "default": "World",
                    "configurable": False
                }
            ]
        )

        for template in ResourceTemplate.objects.filter(
                name="mtemplate"
        ).all():
            rs.resource_templates.add(template)

        ser = Service.objects.create(name="A service")
        ser.resource_services.add(rs)

        data = {
            "reference": "TEST-1",
            "service": ser.id,
            "template_fields": {
                Node.objects.get().hostname: {

                }
            }
        }

        url = reverse("configuration:service_order_list")
        response = self.client.post(url, data, format="json")

        id = response.data['id']

        config_url = reverse("configuration:service_config_view", kwargs={"pk": id})

        config_response = self.client.get(config_url, format='json')
        expected = """Further content:
template2: Hello
template3: Hello World

Nothing more here."""
        self.assertEqual(config_response.data[0]['service_up'], expected)

    def test_subtemplates_exclude(self):
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        template1 = """{{! maintemplate }}
Further content:
{{! subtemplates }}
Nothing more here.
"""
        template2 = "template2: {{ var1 }}"
        template3 = "template3: {{ var1 }} {{ var2 }}"
        template4 = "template4: {{ var1 }} {{! subexclude }}"

        templates = [template1, template2, template3, template4]
        for template in templates:
            data = {
                "name": "mtemplate",
                "up_contents": template,
                "down_contents": "nothing"
            }

            url = reverse("configuration:resource_template_list")
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rs = ResourceService.objects.create(
            name="Test",
            node=Node.objects.get(),
            defaults=[
                {
                    "field": "var1",
                    "default": "Hello",
                    "configurable": False
                },
                {
                    "field": "var2",
                    "default": "World",
                    "configurable": False
                }
            ]
        )

        for template in ResourceTemplate.objects.filter(
                name="mtemplate"
        ).all():
            rs.resource_templates.add(template)

        ser = Service.objects.create(name="A service")
        ser.resource_services.add(rs)

        data = {
            "reference": "TEST-1",
            "service": ser.id,
            "template_fields": {
                Node.objects.get().hostname: {

                }
            }
        }

        url = reverse("configuration:service_order_list")
        response = self.client.post(url, data, format="json")

        id = response.data['id']

        config_url = reverse("configuration:service_config_view", kwargs={"pk": id})

        config_response = self.client.get(config_url, format='json')
        expected = """Further content:
template2: Hello
template3: Hello World

Nothing more here.
template4: Hello """
        self.assertEqual(config_response.data[0]['service_up'], expected)
