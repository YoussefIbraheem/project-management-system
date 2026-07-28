from typing import Any


def document(
    request_schema: type[Any] | None = None,
    response_schema: type[Any] | None = None,
    query_params: list[dict] | None = None,
):
    def decorator(func):
        func._openapi_metadata = {
            "request_schema": request_schema,
            "response_schema": response_schema,
            "query_params": query_params,
        }
        return func

    return decorator
