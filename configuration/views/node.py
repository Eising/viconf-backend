""" This is views for the node/group model """


from configuration.models import Node, Group
from configuration.serializers import NodeSerializer, GroupSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny


class NodeList(generics.ListCreateAPIView):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [AllowAny]
    lookup_field = "hostname"


class NodeView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [AllowAny]
    lookup_field = "hostname"


class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]
    lookup_field = "name"
