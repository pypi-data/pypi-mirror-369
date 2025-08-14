"""
TNNT Auth Templates URL Configuration
"""

# Django
from django.urls import include, path

# AA Templates: Terra Nanotech
from tnnt_templates import views
from tnnt_templates.constants import INTERNAL_URL_PREFIX

app_name: str = "tnnt_templates"

internal_urls = [
    path(
        route="ajax/task_queue_status/",
        view=views.ajax_get_task_queue_status,
        name="ajax_get_task_queue_status",
    ),
]

urlpatterns = [
    # Internal URLs
    path(route=f"{INTERNAL_URL_PREFIX}/", view=include(internal_urls)),
]
