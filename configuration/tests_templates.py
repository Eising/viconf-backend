from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from configuration.models import ResourceTemplate
from django.contrib.auth.models import User


class ResourceTemplateTests(APITestCase):
    fixtures = ['user']

    def test_create_template(self):
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
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
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
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
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
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

        fs_update_response = self.client.put(
            fieldset_url, fieldset, format='json'
        )
        self.assertEqual(fs_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResourceTemplate.objects.get().labels['variable'],
                         'TestVariable')

    def test_update_template(self):
        """ This tests template update """

        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        up_template = "template has {{ var1 }} and {{ var2 }}"
        down_template = "nothing"

        data = {
            "name": "template1",
            "up_contents": up_template,
            "down_contents": down_template
        }
        url = reverse("configuration:resource_template_list")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Get the fieldset
        fieldset_url = reverse('configuration:resource_template_fieldset', kwargs={"pk": response.data['id']})
        fs_response = self.client.get(fieldset_url)
        self.assertEqual(fs_response.status_code, status.HTTP_200_OK)
        fields = [field["name"] for field in fs_response.data["resource_fieldset"]]
        self.assertIn("var1", fields)
        self.assertIn("var2", fields)
        # Update the template
        up_template = "Template has {{ var1 }} and {{ var3 }}"
        new_data = {
            "name": "template1",
            "up_contents": up_template,
            "down_contents": down_template
        }

        template_url = reverse("configuration:resource_template_view", kwargs={"pk": response.data["id"]})
        template_response = self.client.put(template_url, new_data)
        self.assertEqual(template_response.status_code, status.HTTP_200_OK)
        fs_response = self.client.get(fieldset_url)
        fields = [field["name"] for field in fs_response.data["resource_fieldset"]]

        self.assertIn("var1", fields)
        self.assertNotIn("var2", fields)
        self.assertIn("var3", fields)
