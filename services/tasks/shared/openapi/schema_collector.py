import pkgutil
import importlib
import inspect


class SchemaCollector:
    """Knows only how to discover and process Pydantic schemas."""
    
    def __init__(self,base_module):
        self.base_module = base_module
        
    def collect(self):
        all_schemas = []
        base_module = importlib.import_module(self.base_module)
        
        for _, module_name, is_pkg in pkgutil.walk_packages(
        base_module.__path__, base_module.__name__ + "."
        ):
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_name and not name.endswith('Base'):
                        all_schemas.append(obj)
            except ImportError:
                continue
        
        return all_schemas