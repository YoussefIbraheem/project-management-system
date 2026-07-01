from pydantic import BaseModel


def document(
    request_schema: BaseModel = None,
    response_schema: BaseModel = None,
    query_params: dict = None,
):
    def decorator(func):
        func._openapi_metadata = {
            "request_schema": request_schema,
            "response_schema": response_schema,
            "query_params": query_params,
        }
        return func

    return decorator
