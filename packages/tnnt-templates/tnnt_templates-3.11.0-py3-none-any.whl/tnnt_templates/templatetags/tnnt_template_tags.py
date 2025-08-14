"""
Template filter for Terra Nanotech templates
"""

# Django
from django.apps import apps
from django.template.defaulttags import register


@register.filter
def startswith(value, arg):
    """
    Usage, {% if value|starts_with:"arg" %}
    """

    return value.startswith(arg)


@register.simple_tag
def is_app_installed(app_name):
    """
    Check if a Django app is installed

    Usage:
    ```django
    {% load my_filters %}

    {% is_app_installed "myapp" as is_myapp_installed %}
    {% if is_myapp_installed %}
        ...
    {% endif %}
    ```
    :param app_name:
    :return:
    """

    return apps.is_installed(app_name)
