import yaml
from .route_collector import RouteCollector
from .schema_collector import SchemaCollector
from pydantic.json_schema import models_json_schema
from app import settings

class OpenAPIDocGenerator:
    def __init__(self, route_collector:RouteCollector, schema_collector:SchemaCollector):
        self.route_collector = route_collector
        self.schema_collector = schema_collector
        
    def generate(self,output_path):
        try:
            routes = self.route_collector.collect()
            schemas = self.schema_collector.collect()
            
            doc = self._build_doc(routes,schemas)
            self._write(doc=doc,output_path=output_path)

        except Exception as e:
            print(f"Error generating OpenAPI documentation: {e}")
    
    def _build_doc(self,routes,schemas):
        _, processed_schemas = models_json_schema(
                [(schema, "validation") for schema in schemas],
                ref_template="#/components/schemas/{model}"
            )

        openapi_schema = {
                "openapi": "3.1.0",
                "info": {
                    "title": f"{settings.SERVICE_NAME} API DOC",
                    "version": "0.0.1",
                },
                "components": {
                    "schemas": processed_schemas.get('$defs', {}),
                },
                "paths": routes,   # ← now a properly structured dict
            }
        
        return openapi_schema
    
    def _write(self, doc: dict, output_path: str):
        with open(output_path, "w") as f:
            f.write(yaml.dump(doc, sort_keys=False))