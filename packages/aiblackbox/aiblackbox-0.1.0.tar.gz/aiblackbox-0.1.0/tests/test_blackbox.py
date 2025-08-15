import os
import unittest
from unittest import mock
import threading
import time
import json

from aiblackbox.blackbox import BlackBox
from aiblackbox import generic_patch

def debug_print(msg, data=None):
    print(f"[DEBUG] {msg}")
    if data is not None:
        print(f"       {data}")

class TestBlackBoxCore(unittest.TestCase):
    def setUp(self):
        self.bb = BlackBox()
        self.bb.clear()
        debug_print("Setup BlackBox and cleared logs")

    def tearDown(self):
        self.bb.clear()
        debug_print("Tore down and cleared logs")

    def test_log_creates_file_and_content(self):
        debug_print("Running test_log_creates_file_and_content")
        self.bb.log(
            input_data={"prompt": "Hello"},
            output_data={"response": "Hi"},
            parameters={"temperature": 0.7},
            metadata={"model": "test-model"}
        )
        self.assertTrue(os.path.exists(self.bb.log_path))
        debug_print(f"Log file created at {self.bb.log_path}")

        with open(self.bb.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)

        try:
            entry = json.loads(lines[0])
        except json.JSONDecodeError:
            # fallback to eval (unsafe, only for tests)
            entry = eval(lines[0])
        debug_print("Log entry content", entry)

        self.assertIn("input_data", entry)
        self.assertEqual(entry["parameters"]["temperature"], 0.7)

    def test_log_handles_non_serializable(self):
        debug_print("Running test_log_handles_non_serializable")

        class NonSerializable:
            pass

        # Should not crash
        try:
            self.bb.log(
                input_data=NonSerializable(),
                output_data=NonSerializable(),
                parameters={},
                metadata={}
            )
            logged = True
        except Exception as e:
            logged = False
            debug_print("Exception during logging non-serializable", str(e))

        self.assertTrue(logged, "Logging failed on non-serializable objects")

    def test_replay_yields_logged_entries(self):
        debug_print("Running test_replay_yields_logged_entries")
        self.bb.log(input_data="in", output_data="out")
        entries = list(self.bb.replay())
        debug_print(f"Replayed entries count: {len(entries)}", entries)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["input_data"], "in")
        self.assertEqual(entries[0]["output_data"], "out")

    def test_replay_handles_corrupt_json(self):
        debug_print("Running test_replay_handles_corrupt_json")

        # Write corrupted JSON line to log file
        with open(self.bb.log_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }\n")

        # Replay should skip or handle error gracefully
        try:
            entries = list(self.bb.replay())
            replayed = True
            debug_print("Replayed entries despite corrupt log", entries)
        except Exception as e:
            replayed = False
            debug_print("Exception during replay of corrupt log", str(e))

        self.assertTrue(replayed, "Replay failed on corrupt JSON")

    def test_clear_deletes_log_file(self):
        debug_print("Running test_clear_deletes_log_file")
        self.bb.log(input_data="a", output_data="b")
        self.assertTrue(os.path.exists(self.bb.log_path))
        debug_print("Log file exists before clear")
        self.bb.clear()
        self.assertFalse(os.path.exists(self.bb.log_path))
        debug_print("Log file successfully deleted after clear")

    def test_concurrent_logging(self):
        debug_print("Running test_concurrent_logging")

        def log_stuff(idx):
            self.bb.log(
                input_data={"thread": idx},
                output_data={"result": idx},
                parameters={},
                metadata={"thread": idx}
            )

        threads = [threading.Thread(target=log_stuff, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        entries = list(self.bb.replay())
        debug_print(f"Entries logged concurrently: {len(entries)}")
        self.assertEqual(len(entries), 10)


class TestGenericPatch(unittest.TestCase):
    def test_patch_function_logs_call(self):
        debug_print("Running TestGenericPatch.test_patch_function_logs_call")
        bb = BlackBox()
        bb.clear()

        def dummy_func(x, y=5):
            return x + y

        wrapped = generic_patch.patch_function(dummy_func, name="dummy_func")
        result = wrapped(10, y=3)
        debug_print("Called patched dummy_func", f"Result={result}")
        self.assertEqual(result, 13)

        entries = list(bb.replay())
        debug_print("Logged entries after patched dummy_func call", entries)
        self.assertTrue(any(e.get("metadata", {}).get("function_name") == "dummy_func" for e in entries))

    def test_patch_function_raises_error(self):
        debug_print("Running TestGenericPatch.test_patch_function_raises_error")
        bb = BlackBox()
        bb.clear()

        def raises(x):
            raise ValueError("fail")

        wrapped = generic_patch.patch_function(raises, name="raises_func")
        with self.assertRaises(ValueError):
            wrapped(1)

        entries = list(bb.replay())
        debug_print("Logged entries after exception in patched function", entries)
        self.assertTrue(any(e.get("metadata", {}).get("function_name") == "raises_func" for e in entries))


class TestOpenAIPatch(unittest.TestCase):
    def setUp(self):
        debug_print("Setting up TestOpenAIPatch")
        import openai

        self.mock_create = mock.Mock(return_value={"id": "fake", "choices": [{"message": {"content": "test"}}]})
        self.original_create = openai.ChatCompletion.create
        openai.ChatCompletion.create = self.mock_create

        patch_openai.apply_patches()

        self.bb = BlackBox()
        self.bb.clear()

    def tearDown(self):
        debug_print("Tearing down TestOpenAIPatch")
        import openai
        openai.ChatCompletion.create = self.original_create
        self.bb.clear()

    def test_openai_patch_logs_call(self):
        debug_print("Running TestOpenAIPatch.test_openai_patch_logs_call")
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello from test"}]
        )
        debug_print("Called patched openai.ChatCompletion.create", f"Response={response}")
        self.assertEqual(response["id"], "fake")

        entries = list(self.bb.replay())
        debug_print("Log entries after openai.ChatCompletion.create call", entries)

        found = False
        for e in entries:
            if e.get("metadata", {}).get("function_name", "").startswith("openai.ChatCompletion.create"):
                found = True
                self.assertIn("args", e["input_data"])
                self.assertIn("kwargs", e["input_data"])
                self.assertEqual(e["output_data"]["id"], "fake")
        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
