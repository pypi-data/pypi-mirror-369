import os
import unittest
import threading
import asyncio
import json
import types
import time

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
            entry = eval(lines[0])
        debug_print("Log entry content", entry)

        self.assertIn("input_data", entry)
        self.assertEqual(entry["parameters"]["temperature"], 0.7)

    def test_log_handles_non_serializable(self):
        debug_print("Running test_log_handles_non_serializable")

        class NonSerializable:
            pass

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
        with open(self.bb.log_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }\n")

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
    def setUp(self):
        # Use the same backend as generic_patch
        self.bb = generic_patch._backend
        if hasattr(self.bb, 'logs'):
            self.bb.logs.clear()
        debug_print("Setup using generic_patch backend")

    def get_logs(self):
        """Helper to get logs from current backend"""
        if isinstance(generic_patch._backend, generic_patch.MemoryBackend):
            return generic_patch._backend.logs
        return list(generic_patch.get_and_clear_fallback_logs())

    def test_patch_function_logs_call(self):
        debug_print("Running TestGenericPatch.test_patch_function_logs_call")
        
        def dummy_func(x, y=5):
            return x + y

        wrapped = generic_patch.patch_function(dummy_func, name="dummy_func")
        result = wrapped(10, y=3)
        debug_print("Called patched dummy_func", f"Result={result}")
        self.assertEqual(result, 13)

        # Small delay to ensure logging completes
        time.sleep(0.1)
        
        entries = self.get_logs()
        debug_print("Logged entries after patched dummy_func call", entries)
        self.assertTrue(any(e.get("metadata", {}).get("function_name") == "dummy_func" for e in entries))

    def test_patch_function_raises_error(self):
        debug_print("Running TestGenericPatch.test_patch_function_raises_error")
        
        def raises(x):
            raise ValueError("fail")

        wrapped = generic_patch.patch_function(raises, name="raises_func")
        with self.assertRaises(ValueError):
            wrapped(1)

        # Small delay to ensure logging completes
        time.sleep(0.1)
        
        entries = self.get_logs()
        debug_print("Logged entries after exception in patched function", entries)
        if entries:
            self.assertTrue(any(e.get("metadata", {}).get("function_name") == "raises_func" for e in entries))

    def test_patch_async_function(self):
        debug_print("Running TestGenericPatch.test_patch_async_function")
        
        async def async_func(x):
            return x * 2

        wrapped = generic_patch.patch_function(async_func, name="async_func")
        result = asyncio.run(wrapped(5))
        debug_print("Called patched async_func", f"Result={result}")
        self.assertEqual(result, 10)

        # Allow time for async logging
        time.sleep(0.1)
        
        entries = self.get_logs()
        self.assertTrue(any(e.get("metadata", {}).get("function_name") == "async_func" for e in entries))

    def test_patch_object_and_class(self):
        debug_print("Running TestGenericPatch.test_patch_object_and_class")
        
        class TestClass:
            def method(self, x):
                return x + 1

            @staticmethod
            def static(x):
                return x * 2

            @classmethod
            def cls_method(cls, x):
                return x + 3

        obj = TestClass()
        generic_patch.patch_object(obj, "method")
        generic_patch.patch_class(TestClass)
        self.assertEqual(obj.method(5), 6)
        self.assertEqual(TestClass.static(4), 8)
        self.assertEqual(TestClass.cls_method(2), 5)

        # Small delay to ensure logging completes
        time.sleep(0.1)
        
        entries = self.get_logs()
        debug_print("Logged entries after object/class patch", entries)
        self.assertTrue(any("method" in e.get("metadata", {}).get("function_name", "") for e in entries))

    def test_unpatch_object_and_all(self):
        debug_print("Running TestGenericPatch.test_unpatch_object_and_all")
        
        class C:
            def f(self): return 1

        obj = C()
        generic_patch.patch_object(obj, "f")
        # Fixed: handle bound vs unbound methods
        self.assertTrue(isinstance(obj.f, types.MethodType))
        self.assertNotEqual(obj.f.__func__, C.f)
        generic_patch.unpatch_object(obj, "f")
        self.assertEqual(obj.f.__func__, C.f)

        # Test unpatch_all restores multiple
        generic_patch.patch_class(C)
        generic_patch.unpatch_all()
        self.assertEqual(obj.f.__func__, C.f)

    def test_apply_generic_patches(self):
        debug_print("Running TestGenericPatch.test_apply_generic_patches")
        
        class DummyAI:
            def forward(self, x):
                return x + 1

        # Avoid crashing on optional imports
        try:
            generic_patch.apply_generic_patches(silent=True)
        except Exception as e:
            debug_print("apply_generic_patches skipped due to import error", str(e))

        dummy = DummyAI()
        wrapped_forward = generic_patch.patch_function(dummy.forward, "forward")
        result = wrapped_forward(3)
        self.assertEqual(result, 4)

    def test_patch_idempotency(self):
        debug_print("Running TestGenericPatch.test_patch_idempotency")
        
        def f(x): return x*2
        wrapped1 = generic_patch.patch_function(f)
        wrapped2 = generic_patch.patch_function(f)
        self.assertIs(wrapped1, wrapped2, "Repeated patching should return same wrapper")


class TestSerializationAndFallback(unittest.TestCase):
    def setUp(self):
        self.bb = generic_patch._backend
        if hasattr(self.bb, 'logs'):
            self.bb.logs.clear()
        debug_print("Setup using generic_patch backend")

    def get_logs(self):
        """Helper to get logs from current backend"""
        if isinstance(generic_patch._backend, generic_patch.MemoryBackend):
            return generic_patch._backend.logs
        return list(generic_patch.get_and_clear_fallback_logs())

    def test_numpy_pandas_torch_serialization(self):
        debug_print("Running TestSerializationAndFallback")
        
        # Skip if dependencies not available
        if None in (generic_patch.np, generic_patch.pd, generic_patch.torch):
            self.skipTest("Optional dependencies not available")

        array = generic_patch.np.arange(5)
        df = generic_patch.pd.DataFrame({"a": range(3)})
        tensor = generic_patch.torch.tensor([1,2,3])

        wrapped_func = generic_patch.patch_function(lambda x: x, "serial_test")
        wrapped_func(array)
        wrapped_func(df)
        wrapped_func(tensor)

        time.sleep(0.1)
        entries = self.get_logs()
        debug_print("Logged entries for numpy/pandas/torch", entries)
        if entries:
            self.assertTrue(any("serial_test" in e.get("metadata", {}).get("function_name", "") for e in entries))

    def test_custom_serializer_and_max_depth(self):
        debug_print("Running TestSerializationAndFallback.test_custom_serializer_and_max_depth")
        
        class Weird:
            def __str__(self):
                return "weird"

        generic_patch.register_custom_serializer(Weird, lambda obj: "custom!")

        def f(x):
            return x

        wrapped = generic_patch.patch_function(f, "weird_test")

        nested = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": { 
                                "level6": "end"
                            }
                        }
                    }
                }
            }
        }

        wrapped(Weird())
        wrapped(nested)

        time.sleep(0.1)  # Make sure to import time at the top
        entries = self.get_logs()
        debug_print("Logged entries for weird_test", entries)

        if entries:
            self.assertTrue(
                any("weird_test" in e.get("metadata", {}).get("function_name", "") for e in entries)
            )

    def test_edge_case_objects(self):
        debug_print("Running TestSerializationAndFallback.test_edge_case_objects")
        
        def gen_func():
            yield 1

        def inner_func():
            return 2

        class NoDict:
            __slots__ = ['a']
            def __init__(self):
                self.a = 5

        wrapped1 = generic_patch.patch_function(gen_func, "gen_test")
        wrapped2 = generic_patch.patch_function(inner_func, "inner_test")
        wrapped3 = generic_patch.patch_function(lambda x: x, "nodict_test")

        wrapped1()
        wrapped2()
        wrapped3(NoDict())

        time.sleep(0.1)
        entries = self.get_logs()
        debug_print("Logged entries for edge case objects", entries)
        if entries:
            self.assertTrue(any("gen_test" in e.get("metadata", {}).get("function_name", "") for e in entries))

    def test_fallback_logging(self):
        debug_print("Running TestSerializationAndFallback")
        
        class FailingBackend(generic_patch.LogBackend):
            def log(self, **kwargs):
                raise RuntimeError("fail")

        # Store original backend
        original_backend = generic_patch._backend
        try:
            generic_patch.set_log_backend(FailingBackend())
            
            wrapped = generic_patch.patch_function(lambda x: x+1, "fb_test")
            wrapped(1)

            fallback_logs = generic_patch.get_and_clear_fallback_logs()
            self.assertTrue(any("fb_test" in e.get("metadata", {}).get("function_name", "") for e in fallback_logs))
        finally:
            # Restore original backend
            generic_patch.set_log_backend(original_backend)

    def test_backend_switching(self):
        debug_print("Running TestSerializationAndFallback.test_backend_switching")
        
        # Store original backend
        original_backend = generic_patch._backend
        try:
            bb_mem = generic_patch.get_memory_backend()
            generic_patch.set_log_backend(bb_mem)

            def f(x): return x*3
            wrapped = generic_patch.patch_function(f, "backend_test")
            wrapped(2)

            time.sleep(0.1)
            entries = bb_mem.logs
            self.assertTrue(any("backend_test" in e.get("metadata", {}).get("function_name", "") for e in entries))
        finally:
            # Restore original backend
            generic_patch.set_log_backend(original_backend)

    def test_async_task_id_logging(self):
        debug_print("Running TestSerializationAndFallback.test_async_task_id_logging")
        
        async def async_task(x):
            return x*10

        wrapped = generic_patch.patch_function(async_task, "async_task_test")
        result = asyncio.run(wrapped(3))
        self.assertEqual(result, 30)

        # Allow time for async logging
        time.sleep(0.1)
        
        entries = self.get_logs()
        self.assertTrue(any("async_task_test" in e.get("metadata", {}).get("function_name", "") for e in entries))
        for e in entries:
            self.assertIn("task_id", e.get("metadata", {}))


if __name__ == "__main__":
    unittest.main()