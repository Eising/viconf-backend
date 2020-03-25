from rest_framework import serializers
from configuration.models import Node, Group


class GroupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        allow_null=True,
        required=False,
    )
    enable_password = serializers.CharField(
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Group
        fields = [
            'name',
            'username',
            'password',
            'enable_password'
        ]


class NodeSerializer(serializers.ModelSerializer):
    group_data = GroupSerializer(source='group', read_only=True)

    class Meta:
        model = Node
        fields = [
            'hostname',
            'ipv4',
            'ipv6',
            'driver',
            'comment',
            'group',
            'group_data'
        ]
