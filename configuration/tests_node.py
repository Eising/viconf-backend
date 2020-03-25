from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from configuration.models import Node, Group


class NodeTests(APITestCase):

    def test_create_group(self):
        data = {
            "name": "test",
            "username": "test",
            "password": "test",
        }
        url = reverse("configuration:grouplist")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.get().name, "test")
        self.assertEqual(Group.objects.get().username, "test")
        self.assertEqual(Group.objects.get().password, "test")
        self.assertEqual(Group.objects.get().enable_password, None)

    def test_create_node(self):
        group = Group.objects.create(
            name="test",
            username="user"
        )

        url = reverse("configuration:nodelist")
        data = {
            "driver": "none",
            "hostname": "test",
            "group": group.name
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Node.objects.count(), 1)
        self.assertEqual(Node.objects.get().hostname, "test")
        self.assertEqual(Node.objects.get().group.name, "test")

    def test_group_list(self):
        group = Group.objects.create(
            name="test",
            username="user"
        )
        Node.objects.create(
            hostname="hostname",
            group=group,
            driver="none"
        )
        url = reverse("configuration:nodelist")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hostname'], "hostname")
        self.assertEqual(response.data[0]['group_data']['username'], "user")
