from pydantic.json_schema import models_json_schema
from flask import Flask
from .path_converter import FlaskPathConverter
from .operations_builder import OperationBuilder
import importlib


class RouteCollector:

    def __init__(
        self,
        app: Flask,
        converter: FlaskPathConverter,

        operations_builder: OperationBuilder,
    ):
        self.app = app
        self.converter = converter
        self.operations_builder = operations_builder

    IGNORED_METHODS = {"HEAD", "OPTIONS"}

    def collect(self) -> dict:
        """
        Iterates Flask's URL map and builds an OpenAPI-compatible 'paths' dict.

        Returns a dict keyed by OpenAPI-style path strings, where each value is
        itself a dict keyed by lowercase HTTP method containing an Operation object.

        e.g. {
            "/pets": {
                "get":  { "operationId": "listPets",  "parameters": [], "responses": {"200": ...} },
                "post": { "operationId": "createPet", "parameters": [], "responses": {"200": ...} },
            },
            "/pets/{pet_id}": {
                "get":  { "operationId": "getPetById", "parameters": [...], "responses": {"200": ...} },
            }
        }
        """
        paths = {}

        with self.app.app_context():
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint == "static":
                    continue

                openapi_path = self.converter.convert(rule.rule)

                if openapi_path not in paths:
                    paths[openapi_path] = {}

                # Each method on this route becomes its own Operation
                for method in rule.methods:
                    if method in self.IGNORED_METHODS:
                        continue

                    endpoint = rule.endpoint.rsplit(".", 1)
                    if len(endpoint) < 2:
                        continue
                    module_name, function_name = endpoint
                    base_module = importlib.import_module(f"app.apis.{module_name}_api")
                    func_data = getattr(base_module, function_name)

                    if func_data:
                        operation = self.operations_builder.build(func_data)
                        
                        paths[openapi_path][method.lower()] = operation

        return paths
