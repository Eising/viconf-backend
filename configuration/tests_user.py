""" Test user views """

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class UserTests(APITestCase):
    fixtures = ['user']

    def test_curuser(self):
        """ Test that we can get the currently logged in user """
        url = reverse("configuration:loggedinuserdetail")
        user = User.objects.get(username='api')
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'api')


    def test_user_not_logged_in(self):
        """ Test that we don't get anything if there's no user logged in """
        url = reverse("configuration:loggedinuserdetail")
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
