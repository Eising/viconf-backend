from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from configuration.models import (
    ResourceTemplate,
    ResourceService,
    Node,
    Service
)


class ServiceTests(APITestCase):
    fixtures = ['nodeandtemplate']

    def test_fixture(self):
        self.assertEqual(ResourceTemplate.objects.count(), 1)

    def test_create_rs(self):

        data = {
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
            node=Node.objects.get(),
            defaults={
                "place": "World",
                "day": "Wednesday"
            }
        )

        rs.resource_templates.add(ResourceTemplate.objects.get())

        data = {
            "name": "A service",
            "resource_services": [
                rs.id
            ]
        }

        url = reverse("configuration:service_list")
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.get().resource_services.count(), 1)
        self.assertEqual(Service.objects.get().name, "A service")

    def test_service_order(self):
        rs = ResourceService.objects.create(
            node=Node.objects.get(),
            defaults={
                "place": "World",
                "day": "Wednesday"
            }
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
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        id = response.data['id']

        config_url = reverse("configuration:service_config_view", kwargs={"pk": id})

        config_response = self.client.get(config_url, format='json')
        self.assertEqual(config_response.data[0]['node'], 'test.node')
