from pathlib import Path

DEFAULT_MODEL_DIRECTORY = Path(__file__).resolve().parent / "models"
REQUEST_METHODS = ["get", "put", "post", "patch", "delete", "download", "all"]

MAPPINGS = {
            "X_API_VERSION": "X-API-VERSION",
            "from_": "from",
            "ids__": "ids[]",
            "jurisdiction__id": "jurisdiction_id",
            "service_type__id": "service_type_id",
            "trigger__id": "trigger_id",
            "close_date__": "close_date",
            "custom_field_ids__": "custom_field_ids[]",
            "exclude_ids__": "exclude_ids[]",
            "pending_date__": "pending_date[]",
            "open_date__": "open_date"
        }

BASE_URL = {
    "us": "https://app.clio.com",
    "au": "https://au.app.clio.com",
    "ca": "https://ca.app.clio.com",
    "eu": "https://eu.app.clio.com"
}

API_VERSION_PATH = {4: "api/v4"}