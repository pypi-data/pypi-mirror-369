import json
import os
import threading
from datetime import datetime
from . import config
from . import utils


def safe_serialize(obj):
    """Attempt to JSON serialize, fallback to string if fails."""
    try:
        # Serialize then deserialize to ensure valid JSON-compatible object
        return json.loads(json.dumps(obj, default=str))
    except (TypeError, OverflowError):
        return str(obj)


class BlackBox:
    """
    Core AI Black Box logger.
    Records all AI model calls, inputs, outputs, parameters, and metadata.
    Thread-safe, lightweight, and uses append-only JSONL logs.
    """

    def __init__(self, log_path=None):
        # Use default log file from config if not provided
        self.log_path = log_path or config.DEFAULT_LOG_PATH
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # Thread lock to prevent race conditions
        self._lock = threading.Lock()

    def _write_log(self, entry):
        """Append a log entry to the JSONL file."""
        with self._lock:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log(self, input_data=None, output_data=None, parameters=None, metadata=None):
        """
        Log a single AI call.
        :param input_data: Raw input(s) sent to the model
        :param output_data: Output(s) returned from the model
        :param parameters: Model parameters (e.g., temperature, max_tokens)
        :param metadata: Any extra metadata (e.g., model name, user ID)
        """
        entry = {
            "timestamp": utils.utc_timestamp(),
            "input_hash": utils.hash_data(input_data),
            "output_hash": utils.hash_data(output_data),
            "input_data": safe_serialize(input_data),
            "output_data": safe_serialize(output_data),
            "parameters": safe_serialize(parameters or {}),
            "metadata": safe_serialize(metadata or {}),
            "version": config.LOG_FORMAT_VERSION
        }
        self._write_log(entry)

    def replay(self):
        """Yield all log entries from the file, skipping corrupted lines."""
        if not os.path.exists(self.log_path):
            return
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[AI BlackBox] Warning: skipping corrupt log line: {line} ({e})")
                    continue

    def clear(self):
        """Delete the log file."""
        with self._lock:
            if os.path.exists(self.log_path):
                os.remove(self.log_path)

    def __repr__(self):
        return f"<BlackBox log_path='{self.log_path}'>"
