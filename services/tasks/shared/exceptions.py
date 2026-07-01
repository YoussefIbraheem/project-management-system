from flask import jsonify


class APIException(Exception):
    """
    Base API exception. Raise subclasses directly in your views/services;
    register handle_api_exception on your Flask app once to catch them all.
    """
    status_code = 400
    default_message = "Bad Request"

    def __init__(self, message: str = None, data: dict = None):
        self.message = message or self.default_message
        self.data = data  # must be a plain dict if provided; never pass an Exception here
        super().__init__(self.message)

    def to_dict(self) -> dict:
        body = {
            "error": {
                "status": self.status_code,
                "message": self.message,
            }
        }
        if self.data:
            body["error"]["details"] = self.data
        return body

    def to_response(self):
        return jsonify(self.to_dict()), self.status_code


# ── Concrete subclasses ────────────────────────────────────────────────────────

class BadRequestException(APIException):
    """Malformed request body or missing required fields (400)."""
    status_code = 400
    default_message = "Bad Request"


class ValidationException(APIException):
    """Input failed schema/business-rule validation (422).

    Pass `data` as a dict of field → error message pairs for fine-grained
    feedback, e.g. {"owner_id": "Field is required"}.
    """
    status_code = 422
    default_message = "Validation Error"


class NotFoundException(APIException):
    """Requested resource does not exist (404)."""
    status_code = 404
    default_message = "Resource Not Found"


class UnauthorizedException(APIException):
    """Missing or invalid authentication credentials (401)."""
    status_code = 401
    default_message = "Unauthorized"


class ForbiddenException(APIException):
    """Authenticated user lacks permission for this action (403)."""
    status_code = 403
    default_message = "Forbidden"


class ConflictException(APIException):
    """State conflict, e.g. duplicate unique field (409)."""
    status_code = 409
    default_message = "Conflict"


class InternalServerException(APIException):
    """Unexpected server-side failure (500)."""
    status_code = 500
    default_message = "Internal Server Error"


# ── Flask error handler — register once in your app factory ───────────────────

def handle_api_exception(e: APIException):
    return e.to_response()


def register_error_handlers(app):
    """
    Call this inside your create_app() factory:

        from shared.exceptions import register_error_handlers
        register_error_handlers(app)
    """
    app.register_error_handler(APIException, handle_api_exception)

    # Catch plain Python exceptions that slipped through so they don't expose
    # a stack trace in production.
    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Unhandled exception: %s", e)
        return InternalServerException().to_response()