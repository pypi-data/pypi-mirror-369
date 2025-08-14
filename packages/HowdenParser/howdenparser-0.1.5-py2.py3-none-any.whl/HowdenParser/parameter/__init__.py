import os
import importlib

# Get all .py files in this folder except __init__.py
current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]  # remove .py
        module = importlib.import_module(f".{module_name}", package=__name__)

        # Add all classes from the module to the package namespace
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type):  # only classes
                globals()[attr_name] = attr