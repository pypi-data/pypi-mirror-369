from .config import *

ENDPOINTS_PATH = TEMP_DIR_PATH / "endpoints.py"

HEADER = """from typing import Dict, Type, Optional
from .query import *  # Import all query models
from .request_body import *  # Import all request body models
from .fields import *

class Endpoints:
    \"\"\"
    Registry for storing endpoint metadata, including paths,
    query models, and request body models.
    \"\"\"

    registry: Dict[str, Dict[str, Optional[Type]]] = {}
"""

def generate_endpoint_registry(endpoints: list):
    """
    Generate the Endpoints class with dynamic registry mapping.

    :param endpoints: List of dictionaries containing endpoint metadata.
    """
    ENDPOINTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write the header if the file doesn't exist
    if not ENDPOINTS_PATH.exists():
        with open(ENDPOINTS_PATH, "w") as f:
            f.write(HEADER)
            f.write("\n")

    # Populate the registry dynamically
    with open(ENDPOINTS_PATH, "a") as f:
        f.write("    @classmethod\n")
        f.write("    def initialize_registry(cls):\n")
        f.write("        \"\"\"\n        Initialize the endpoint registry dynamically.\n        \"\"\"\n")
        for endpoint in endpoints:
            name = endpoint["name"]
            path = endpoint["path"]
            method = endpoint["method"].upper()
            query_model = endpoint.get("query_model", "None")
            request_body_model = endpoint.get("request_body_model", "None")
            field_model = endpoint.get("field_model", "None")

            # Check if endpoint qualifies as a download
            status_codes = endpoint.get("responses", {})
            is_download = method == "GET" and "303" in status_codes.keys()

            # Set the method to DOWNLOAD if applicable
            if is_download:
                method = "DOWNLOAD"

            # Write the registry entry
            f.write(f"        cls.registry['{name}'] = {{\n")
            f.write(f"            'path': '{path}',\n")
            f.write(f"            'method': '{method}',\n")
            f.write(f"            'query_model': {query_model},\n")
            f.write(f"            'request_body_model': {request_body_model},\n")
            f.write(f"            'field_model': {field_model}\n")
            f.write("        }\n")
        f.write("\n")
        f.write("        # Initialize the registry\n")
        f.write("Endpoints.initialize_registry()\n")
        
    print(f"Dataclasses generated in {ENDPOINTS_PATH}")