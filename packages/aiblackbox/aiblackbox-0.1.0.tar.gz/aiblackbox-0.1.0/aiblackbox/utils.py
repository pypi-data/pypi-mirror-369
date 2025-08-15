import hashlib
import json
from datetime import datetime, timezone

def utc_timestamp():
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def hash_data(data):
    """Return SHA256 hash of data (JSON-serialized)."""
    try:
        encoded = json.dumps(data, sort_keys=True).encode("utf-8")
    except (TypeError, ValueError):
        encoded = str(data).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
