import re

class FlaskPathConverter:
    """Knows only how to convert Flask path syntax to OpenAPI syntax."""
    
    CONVERTER_MAP = {
        "int":    {"type": "integer", "format": "int64"},
        "float":  {"type": "number",  "format": "float"},
        "string": {"type": "string"},
        "uuid":   {"type": "string",  "format": "uuid"},
    }
    def convert(self,flask_path: str) -> tuple[str, list[dict]]:
        """
        Converts Flask path syntax to OpenAPI path syntax and extracts path parameters.

        e.g. /pets/<int:pet_id>  →  ("/pets/{pet_id}", [{"name": "pet_id", "in": "path", ...}])
        /pets/<pet_id>      →  ("/pets/{pet_id}", [{"name": "pet_id", "in": "path", ...}])
        """
        parameters = []

        # Match both typed (<int:name>) and untyped (<name>) converters
        pattern = re.compile(r"<(?:(\w+):)?(\w+)>")

        
        def replace_param(match):
            converter = match.group(1) or "string"  # default to string if no type given
            param_name = match.group(2)

            schema = self.CONVERTER_MAP.get(converter, {"type": "string"})
            parameters.append({
                "name": param_name,
                "in": "path",
                "required": True,               # path params are always required in OpenAPI
                "schema": schema,
            })
            return f"{{{param_name}}}"
        
        
        openapi_path = pattern.sub(replace_param, flask_path)
        return openapi_path