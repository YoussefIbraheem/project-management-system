import inspect

class OperationBuilder:

    def build(self, func_data):
        parameters = []
        properties = {}
        
        path_parameters = inspect.signature(func_data).parameters
        path_parameters = dict(path_parameters) if path_parameters else {}
        
        
        pydantic_metadata = func_data.__dict__.get("_openapi_metadata", {})
        
        
        request_schema = pydantic_metadata.get("request_schema", None)
        response_schema = pydantic_metadata.get("response_schema", None)

        body_parameters = (
            request_schema.model_json_schema()["properties"] if request_schema else {}
        )
        
        query_parameters = pydantic_metadata.get("query_params", [])
        
        
        request_body_temp = {
            "required": True,
            "description": "description",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": properties,
                    }
                }
            },
        }
        
        if path_parameters:
            
            for param_name, param in path_parameters.items():
                new_param = {
                    "in": "path",
                    "name": param_name,
                    "description": "",
                    "required": True,
                    "schema": {"type": "string"},
                }
                parameters.append(new_param)


        if query_parameters:
            for param in query_parameters:
                new_param = {
                    "in": "query",
                    "name": param.get("name", ""),
                    "description": param.get("description", ""),
                    "required": param.get("required", False),
                    "schema": {
                        "type": param.get("type", "string"),
                    },
                }
                parameters.append(new_param)
                
        tag = func_data.__module__.split(".")[-1] 
        
        operation = {
            # endpoint name is the view function name — use it as operationId
            "operationId": pydantic_metadata.get("operation_id", ""),
            "tags": [tag] if tag else [],
            "parameters": parameters,
            "responses": {"200": {"description": "Successful Response"}},
        }

        if body_parameters:
            for prop_name, prop_info in body_parameters.items():
                properties[prop_name] = {"type": prop_info.get("type", "string"),}
                
            
            operation["requestBody"] = request_body_temp

        return operation
