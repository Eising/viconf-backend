from django.db import models
from django.contrib.postgres.fields import JSONField


class Group(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    username = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    enable_password = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class Node(models.Model):
    DRIVERS = (
        ('eos', 'Arista EOS'),
        ('junos', 'Juniper JUNOS'),
        ('iosxr', 'Cisco IOS-XR'),
        ('nxos', 'Cisco NXOS'),
        ('ios', 'Cisco IOS'),
        ('none', 'No driver')
    )

    hostname = models.CharField(max_length=255, primary_key=True)
    ipv4 = models.GenericIPAddressField(protocol="IPv4", null=True, blank=True)
    ipv6 = models.GenericIPAddressField(protocol="IPv6", null=True, blank=True)
    driver = models.CharField(max_length=255, choices=DRIVERS)
    comment = models.TextField(null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    site = models.CharField(max_length=255)


class ResourceTemplate(models.Model):
    """ A resource template is one single resource """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    platform = models.CharField(max_length=255,  null=True)
    up_contents = models.TextField()
    down_contents = models.TextField()
    fields = JSONField(null=True)
    labels = JSONField(null=True)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ResourceService(models.Model):
    """Resource Services collectiions of Templates optionally with node
    and defaults"""
    name = models.CharField(max_length=255)
    resource_templates = models.ManyToManyField(ResourceTemplate)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        null=True
    )
    defaults = JSONField()
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)


class Service(models.Model):
    """A customer service contains one more more Resource Services"""
    name = models.CharField(max_length=255)
    resource_services = models.ManyToManyField(ResourceService)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ServiceOrder(models.Model):
    """ Service is a provisioned service """
    reference = models.CharField(max_length=255)
    customer = models.CharField(max_length=255, null=True)
    location = models.CharField(max_length=255, null=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True
    )
    template_fields = JSONField()
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reference
