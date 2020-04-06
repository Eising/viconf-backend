from rest_framework.response import Response
from rest_framework import status


class SafeDestroyModelMixin:
    """ set deleted instead of deleting the object """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()
