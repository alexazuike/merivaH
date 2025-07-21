from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail
from http import HTTPStatus
from typing import Any, Dict
from rest_framework.response import Response

from api.includes import exceptions


def api_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """Custom API exception handler."""

    error_payload = {"status_code": 0, "message": "", "details": []}

    response = exception_handler(exc, context)
    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        http_code_to_message = {v.value: v.description for v in HTTPStatus}
        status_code = response.status_code
        error_payload["status_code"] = status_code
        error_payload["message"] = http_code_to_message[status_code]
        error_payload["details"] = response.data
        response.data = error_payload
        return Response(error_payload, status=error_payload["status_code"])

    error_payload["status_code"] = 500
    error_payload["message"] = str(exc)

    if type(exc) in [exceptions.ExistingDataException, exceptions.BadRequest]:
        error_payload["status_code"] = 400
        error_payload["message"] = exc.message

    if type(exc) in [exceptions.NotFoundException]:
        error_payload["status_code"] = 404
        error_payload["message"] = exc.message

    if type(exc) in [exceptions.PermissionDenied]:
        error_payload["status_code"] = 403
        error_payload["message"] = exc.message

    if type(exc) in [exceptions.DatabaseException, exceptions.ServerError]:
        error_payload["status_code"] = 500
        error_payload["message"] = exc.message

    return Response(error_payload, status=error_payload["status_code"])
