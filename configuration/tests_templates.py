from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from configuration.models import ResourceTemplate


class ResourceTemplateTests(APITestCase):

    def test_create_template(self):
        up_template = """
Here is a template.
It contains a {{ variable }}"""
        down_template = """
Something {{ variable }}"""

        data = {
            "name": "templatename",
            "up_contents": up_template,
            "down_contents": down_template,
        }

        url = reverse("configuration:resource_template_list")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceTemplate.objects.count(), 1)
        self.assertEqual(ResourceTemplate.objects.get().fields.get(
            'variable'), 'none'
        )
        self.assertEqual(ResourceTemplate.objects.get().labels.get(
            'variable'), 'Variable'
        )

    def test_get_fieldset(self):
        up_template = """
Here is a template.
It contains a {{ variable }}"""
        down_template = """
Something {{ variable }}"""

        data = {
            "name": "templatename",
            "up_contents": up_template,
            "down_contents": down_template,
        }

        url = reverse("configuration:resource_template_list")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceTemplate.objects.count(), 1)
        # Get the fieldset
        fieldset_url = reverse('configuration:resource_template_fieldset', kwargs={"pk": response.data['id']})
        fs_response = self.client.get(fieldset_url)

        self.assertEqual(fs_response.status_code, status.HTTP_200_OK)
        self.assertEqual(fs_response.data['resource_fieldset'][0]['label'],
                         'Variable')

    def test_update_fieldset(self):
        up_template = """
Here is a template.
It contains a {{ variable }}"""
        down_template = """
Something {{ variable }}"""

        data = {
            "name": "templatename",
            "up_contents": up_template,
            "down_contents": down_template,
        }

        url = reverse("configuration:resource_template_list")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceTemplate.objects.count(), 1)
        # Get the fieldset
        fieldset_url = reverse('configuration:resource_template_fieldset', kwargs={"pk": response.data['id']})
        fs_response = self.client.get(fieldset_url)
        self.assertEqual(fs_response.status_code, status.HTTP_200_OK)

        fieldset = {
            "resource_fieldset": [
                {
                    "name": "variable",
                    "validator": "string",
                    "label": "TestVariable"
                }
            ]
        }

        fs_update_response = self.client.post(
            fieldset_url, fieldset, format='json'
        )
        self.assertEqual(fs_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourceTemplate.objects.get().labels['variable'],
                         'TestVariable')
