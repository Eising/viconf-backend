from django.urls import path
from configuration.views import node, services

app_name = 'configuration'

urlpatterns = [
    path(
        "nodes/",
        node.NodeList.as_view(),
        name="nodelist",
    ),
    path(
        "nodes/<str:hostname>/",
        node.NodeView.as_view(),
        name="nodeview",
    ),
    path(
        "groups/",
        node.GroupList.as_view(),
        name="grouplist",
    ),
    path(
        "groups/<str:name>/",
        node.GroupList.as_view(),
        name="groupview",
    ),
    path(
        "resource_templates/",
        services.ResourceTemplateList.as_view(),
        name="resource_template_list",
    ),
    path(
        "resource_templates/<int:pk>/",
        services.ResourceTemplateView.as_view(),
        name="resource_template_view",
    ),
    path(
        "resource_templates/<int:pk>/fields/",
        services.ResourceTemplateFieldsetView.as_view(),
        name="resource_template_fieldset",
    ),
    path(
        "resource_services/",
        services.ResourceServiceList.as_view(),
        name="resource_service_list",
    ),
    path(
        "resource_services/<int:pk>/",
        services.ResourceServiceView.as_view(),
        name="resource_service_view",
    ),
    path(
        "services/",
        services.ServiceList.as_view(),
        name="service_list",
    ),
    path(
        "services/<int:pk>/",
        services.ServiceView.as_view(),
        name="service_view",
    ),
    path(
        "orders/",
        services.ServiceOrderList.as_view(),
        name="service_order_list",
    ),
    path(
        "orders/<int:pk>/",
        services.ServiceOrderView.as_view(),
        name="service_order_view",
    ),
    path(
        "orders/<int:pk>/config/",
        services.ServiceConfigView.as_view(),
        name="service_config_view",
    ),

]
