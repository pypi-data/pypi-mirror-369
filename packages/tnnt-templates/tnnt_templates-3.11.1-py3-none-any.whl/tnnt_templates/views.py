"""
TNNT Auth Templates views module
"""

# Django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

# Alliance Auth
from allianceauth.authentication.core.celery_workers import (
    active_tasks_count,
    queued_tasks_count,
)
from allianceauth.templatetags.admin_status import _celery_stats


@login_required
def ajax_get_task_queue_status(request: WSGIRequest):  # pylint: disable=unused-argument
    """
    AJAX view to get the status of the task queue.
    """

    data = _celery_stats()
    data.update(
        {"tasks_running": active_tasks_count(), "tasks_queued": queued_tasks_count()}
    )
    return JsonResponse(data)
