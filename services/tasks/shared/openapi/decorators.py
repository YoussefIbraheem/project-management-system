from pydantic import BaseModel


def document(
    request_schema: BaseModel | None = None,
    response_schema: BaseModel | None = None,
    query_params: dict | None = None,
):
    def decorator(func):
        func._openapi_metadata = {
            "request_schema": request_schema,
            "response_schema": response_schema,
            "query_params": query_params,
        }
        return func

    return decorator
