# aiblackbox/generic_patch.py
"""
Enhanced universal patcher for AI BlackBox with:
- Reliable logging with fallback
- Concurrency support
- Enhanced metadata
- Custom serialization
- Configurable backends
- Auto-unpatch
- AI function detection
"""

import functools
import types
import inspect
import traceback
import json
import logging
import threading
import os
import sys
import asyncio
import weakref
import importlib
import atexit
import time
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Set, Union, Tuple, Type

# Optional libs
try:
    import pandas as pd
except Exception:
    pd = None

try:
    import numpy as np
except Exception:
    np = None

try:
    import torch
except Exception:
    torch = None

# Global configuration
MAX_DEPTH = 5
MAX_PREVIEW_ROWS = 50
MAX_PREVIEW_ITEMS = 200
_custom_serializers: Dict[type, Callable[[Any], Any]] = {}
_backend = None
_object_patches: List[Tuple[weakref.ref, str, Any]] = []
_fallback_logs: List[Dict[str, Any]] = []
_fallback_lock = threading.Lock()
_env_logged = False
_patch_applied = False


# ------------------ Memory Backend ------------------

class LogBackend:
    """Base class for log backends."""
    def log(self, **kwargs) -> None:
        raise NotImplementedError()

class MemoryBackend(LogBackend):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs = []
            cls._instance.lock = threading.Lock()
        return cls._instance

    def log(self, **kwargs) -> None:
        with self.lock:
            self.logs.append(kwargs)

# ------------------ Global backend instance ------------------

_backend: LogBackend = MemoryBackend()

def set_log_backend(backend: LogBackend) -> None:
    global _backend
    _backend = backend

def get_memory_backend() -> MemoryBackend:
    return MemoryBackend()

# ------------------ Logging / Serialization helpers ------------------

MAX_DEPTH: int = 5
_custom_serializers: Dict[type, Callable[[Any], Any]] = {}
_fallback_logs: List[Dict[str, Any]] = []
_fallback_lock = threading.Lock()

def set_max_depth(depth: int) -> None:
    global MAX_DEPTH
    MAX_DEPTH = depth

def register_custom_serializer(type_: type, func: Callable[[Any], Any]) -> None:
    _custom_serializers[type_] = func

def get_and_clear_fallback_logs() -> List[Dict[str, Any]]:
    global _fallback_logs
    with _fallback_lock:
        logs = _fallback_logs[:]
        _fallback_logs = []
        return logs

# ------------------ Patch tracking globals ------------------

_object_patches: List[Tuple[weakref.ref, str, Any]] = []
_wrapped_registry: Dict[int, Callable] = {}
_originals: Dict[int, Callable] = {}
_patch_applied: bool = False

# ------------------ Patching utilities ------------------

def unpatch_object(obj: Any, attr_name: str) -> bool:
    """Restore a single patched attribute on an object."""
    global _object_patches
    ref = weakref.ref(obj)
    for i, (r, aname, orig) in enumerate(_object_patches):
        if r == ref and aname == attr_name:
            obj_ = r()
            if obj_ is not None:
                setattr(obj_, aname, orig)
            del _object_patches[i]
            return True
    return False

def unpatch_all() -> None:
    global _object_patches, _wrapped_registry, _originals, _patch_applied
    for r, aname, orig in _object_patches[:]:
        obj = r()
        if obj is not None:
            try:
                setattr(obj, aname, orig)
            except Exception:
                pass
    _object_patches.clear()
    _wrapped_registry.clear()
    _originals.clear()
    _patch_applied = False

# Register cleanup on exit
atexit.register(unpatch_all)

# ------------------ Logger setup ------------------

logger = logging.getLogger("aiblackbox.patch")
logger.addHandler(logging.NullHandler())


# ---------------------
# Environment logging
# ---------------------
def _log_environment():
    global _env_logged
    if _env_logged:
        return
        
    env_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "os": os.name,
        "numpy_version": getattr(np, '__version__', None) if np else None,
        "pandas_version": getattr(pd, '__version__', None) if pd else None,
        "torch_version": getattr(torch, '__version__', None) if torch else None,
    }
    
    try:
        _backend.log(
            input_data=None,
            output_data=None,
            parameters=None,
            metadata={"env_info": env_info, "log_type": "environment"}
        )
    except Exception:
        pass
        
    _env_logged = True

# ---------------------
# Serialization helpers
# ---------------------
def _truncate_list(lst: List[Any], limit: int = MAX_PREVIEW_ITEMS) -> List[Any]:
    if len(lst) > limit:
        return lst[:limit] + [f"...({len(lst)-limit} items truncated)"]
    return lst

def safe_serialize(data: Any, depth: int = 0) -> Any:
    """Convert objects to JSON-serializable forms with depth control."""
    if depth > MAX_DEPTH:
        return f"...(max depth {MAX_DEPTH} reached)"
    
    # Check custom serializers
    for t, serializer in _custom_serializers.items():
        if isinstance(data, t):
            return serializer(data)
    
    # Try JSON serialization first
    try:
        json.dumps(data)
        return data
    except (TypeError, OverflowError):
        pass

    # Handle special types
    if pd is not None and isinstance(data, pd.DataFrame):
        try:
            rows = len(data)
            if rows > MAX_PREVIEW_ROWS:
                preview = data.head(10).to_dict(orient="records")
                return {
                    "_pandas_preview": safe_serialize(preview, depth+1),
                    "_pandas_rows": rows,
                    "_pandas_columns": list(data.columns),
                }
            return data.to_dict(orient="records")
        except Exception:
            pass

    if pd is not None and isinstance(data, pd.Series):
        return data.to_dict()
        
    if np is not None and isinstance(data, (np.ndarray, np.generic)):
        try:
            lst = data.tolist()
            return safe_serialize(lst, depth+1)
        except Exception:
            pass
            
    if torch is not None and hasattr(data, "detach") and callable(data.detach):
        try:
            return safe_serialize(data.detach().cpu().tolist(), depth+1)
        except Exception:
            pass
            
    # Handle collections
    if isinstance(data, dict):
        return {k: safe_serialize(v, depth+1) for k, v in data.items()}
        
    if isinstance(data, (list, tuple, set)):
        lst = [safe_serialize(item, depth+1) for item in data]
        return _truncate_list(lst)
        
    # Handle objects with __dict__
    if hasattr(data, "__dict__"):
        try:
            return safe_serialize(vars(data), depth+1)
        except Exception:
            pass
            
    # Fallback to string representation
    try:
        return str(data)
    except Exception:
        return repr(data)

# ---------------------
# Metadata helpers
# ---------------------
def _get_function_module_name(func: Callable) -> str:
    try:
        mod = inspect.getmodule(func)
        return mod.__name__ if mod is not None else "unknown"
    except Exception:
        return "unknown"

def get_call_metadata(func: Callable, name: str, call_seq: int) -> Dict[str, Any]:
    try:
        module = _get_function_module_name(func)
    except Exception:
        module = "unknown"
        
    try:
        file = inspect.getfile(func) if hasattr(func, "__code__") else None
    except Exception:
        file = None
        
    try:
        line = func.__code__.co_firstlineno if hasattr(func, "__code__") else None
    except Exception:
        line = None
        
    try:
        signature = str(inspect.signature(func))
    except Exception:
        signature = "unknown"

    # Get context identifiers
    thread_id = threading.get_ident()
    process_id = os.getpid()
    task_id = None
    try:
        task = asyncio.current_task()
        if task is not None:
            task_id = getattr(task, 'get_name', lambda: None)() or id(task)
    except Exception:
        pass

    return {
        "function_name": name,
        "module": module,
        "file": file,
        "line_number": line,
        "signature": signature,
        "is_coroutine": inspect.iscoroutinefunction(func),
        "is_method": inspect.ismethod(func) or "." in name,
        "call_seq": int(call_seq),
        "thread_id": thread_id,
        "process_id": process_id,
        "task_id": task_id,
    }

# ---------------------
# Per-wrapper ordering closure helper
# ---------------------
def _make_ordered_logger():
    """Create per-wrapper ordering structures."""
    lock = threading.Lock()
    pending_lock = threading.Lock()
    next_seq = 0
    next_flush = 0
    pending: Dict[int, Dict[str, Any]] = {}

    def next_sequence() -> int:
        nonlocal next_seq
        with lock:
            seq = next_seq
            next_seq += 1
            return seq

    def enqueue_and_flush(seq: int, bb_kwargs: Dict[str, Any]):
        nonlocal next_flush
        with pending_lock:
            pending[seq] = bb_kwargs
            # Flush contiguous sequences
            while next_flush in pending:
                item = pending.pop(next_flush)
                try:
                    _backend.log(**item)
                except Exception as e:
                    logger.error("Logging failed: %s", e)
                    with _fallback_lock:
                        _fallback_logs.append(item)
                next_flush += 1

    return next_sequence, enqueue_and_flush

# ---------------------
# Core wrapper
# ---------------------
# In the patch_function function:

def patch_function(func: Callable, name: Optional[str] = None, depth: Optional[int] = None) -> Callable:
    """Wrap a callable to log every invocation."""
    if not callable(func):
        raise TypeError("patch_function expects a callable")

    orig_id = id(func)
    if orig_id in _wrapped_registry:
        return _wrapped_registry[orig_id]

    func_name = name or getattr(func, "__qualname__", getattr(func, "__name__", str(func)))
    next_seq, enqueue_and_flush = _make_ordered_logger()
    _log_environment()
    effective_depth = depth if depth is not None else MAX_DEPTH

    def _safe_get_metadata(seq: int) -> Dict[str, Any]:
        """Always return at least function_name, even if other metadata fails"""
        try:
            metadata = get_call_metadata(func, func_name, seq)
            if not metadata.get("function_name"):
                metadata["function_name"] = func_name
            return metadata
        except Exception as e:
            logger.error("Error getting metadata for %s: %s", func_name, e)
            return {"function_name": func_name}

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        seq = next_seq()
        exception_info = None
        result = None
        start_time = time.time()
        
        try:
            # Get input data
            try:
                bound = inspect.signature(func).bind(*args, **kwargs)
                bound.apply_defaults()
                input_data = dict(bound.arguments)
            except Exception:
                input_data = {"args": args, "kwargs": kwargs}

            # Call original function
            result = func(*args, **kwargs)
            return result
            
        except Exception as ex:
            exception_info = {
                "type": type(ex).__name__,
                "message": str(ex),
                "traceback": traceback.format_exc()
            }
            raise
            
        finally:
            # Always create log entry, even if parts fail
            try:
                duration = time.time() - start_time
                metadata = _safe_get_metadata(seq)
                metadata.update({
                    "duration": duration,
                    "success": exception_info is None
                })

                bb_kwargs = {
                    "input_data": safe_serialize(input_data, depth=effective_depth),
                    "output_data": safe_serialize(result, depth=effective_depth),
                    "parameters": safe_serialize(kwargs, depth=effective_depth),
                    "metadata": safe_serialize(metadata, depth=effective_depth),
                }
                
                if exception_info:
                    bb_kwargs["exception"] = exception_info
                    bb_kwargs["metadata"]["exception"] = exception_info
                    
                enqueue_and_flush(seq, bb_kwargs)
                
            except Exception as e:
                logger.error("Critical logging error for %s: %s", func_name, e)
                # Create minimal log entry if everything else fails
                enqueue_and_flush(seq, {
                    "metadata": {"function_name": func_name, "error": "logging_failed"}
                })

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        seq = next_seq()
        exception_info = None
        result = None
        start_time = time.time()
        
        try:
            # Get input data
            try:
                bound = inspect.signature(func).bind(*args, **kwargs)
                bound.apply_defaults()
                input_data = dict(bound.arguments)
            except Exception:
                input_data = {"args": args, "kwargs": kwargs}

            # Call original function
            result = await func(*args, **kwargs)
            return result
            
        except Exception as ex:
            exception_info = {
                "type": type(ex).__name__,
                "message": str(ex),
                "traceback": traceback.format_exc()
            }
            raise
            
        finally:
            # Always create log entry, even if parts fail
            try:
                duration = time.time() - start_time
                metadata = _safe_get_metadata(seq)
                
                # Get async task info
                try:
                    task = asyncio.current_task()
                    if task is not None:
                        metadata["task_id"] = getattr(task, 'get_name', lambda: None)() or id(task)
                except Exception:
                    pass
                
                metadata.update({
                    "duration": duration,
                    "success": exception_info is None
                })

                bb_kwargs = {
                    "input_data": safe_serialize(input_data, depth=effective_depth),
                    "output_data": safe_serialize(result, depth=effective_depth),
                    "parameters": safe_serialize(kwargs, depth=effective_depth),
                    "metadata": safe_serialize(metadata, depth=effective_depth),
                }
                
                if exception_info:
                    bb_kwargs["exception"] = exception_info
                    bb_kwargs["metadata"]["exception"] = exception_info
                    
                enqueue_and_flush(seq, bb_kwargs)
                
            except Exception as e:
                logger.error("Critical async logging error for %s: %s", func_name, e)
                # Create minimal log entry if everything else fails
                enqueue_and_flush(seq, {
                    "metadata": {"function_name": func_name, "error": "logging_failed"}
                })

    wrapper = async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    _wrapped_registry[orig_id] = wrapper
    _originals[id(wrapper)] = func
    return wrapper

# ---------------------
# Object/Module/Class patchers
# ---------------------
def _resolve_obj_name(obj: Any) -> str:
    if isinstance(obj, ModuleType):
        return obj.__name__
    if hasattr(obj, '__class__'):
        return obj.__class__.__name__
    return "object"

def patch_object(obj: Any, attr_name: str, depth: Optional[int] = None):
    """Patch attribute on object."""
    if not hasattr(obj, attr_name):
        raise AttributeError(f"{obj} has no attribute '{attr_name}'")

    original = getattr(obj, attr_name)
    # Determine correct function_name for tests:
    if inspect.isclass(obj):
        name = f"{obj.__name__}.{attr_name}"
    elif isinstance(obj, ModuleType):
        name = f"{obj.__name__}.{attr_name}"
    else:
        obj_name = _resolve_obj_name(obj)
        name = f"{obj_name}.{attr_name}"

    # Handle bound methods
    if inspect.ismethod(original) and hasattr(original, '__self__'):
        # Create a bound method with the wrapper
        wrapper = patch_function(original.__func__, name=name, depth=depth)
        wrapped = types.MethodType(wrapper, original.__self__)
    else:
        # Regular function or unbound method
        wrapped = patch_function(original, name=name, depth=depth)

    setattr(obj, attr_name, wrapped)
    _object_patches.append((weakref.ref(obj), attr_name, original))
    
def patch_module(module: Union[ModuleType, Any], function_names: List[str], depth: Optional[int] = None):
    """Patch multiple functions on a module."""
    for fname in function_names:
        patch_object(module, fname, depth=depth)

def patch_class(cls: type, exclude: Optional[List[str]] = None, skip_dunder: bool = True, depth: Optional[int] = None):
    """Patch methods of a class safely, with fallback for built-ins."""
    exclude_set = set(exclude or [])
    
    for name in dir(cls):
        if name in exclude_set:
            continue
        if skip_dunder and name.startswith("__") and name.endswith("__"):
            continue
        
        try:
            attr_static = inspect.getattr_static(cls, name)
        except AttributeError:
            continue

        # Skip properties
        if isinstance(attr_static, property):
            continue

        try:
            if isinstance(attr_static, staticmethod):
                original = attr_static.__func__
                wrapped = patch_function(original, f"{cls.__name__}.{name}", depth=depth)
                setattr(cls, name, staticmethod(wrapped))
                try:
                    _object_patches.append((weakref.ref(cls), name, attr_static))
                except TypeError:
                    _object_patches.append((lambda cls=cls: cls, name, attr_static))
            elif isinstance(attr_static, classmethod):
                original = attr_static.__func__
                wrapped = patch_function(original, f"{cls.__name__}.{name}", depth=depth)
                setattr(cls, name, classmethod(wrapped))
                try:
                    _object_patches.append((weakref.ref(cls), name, attr_static))
                except TypeError:
                    _object_patches.append((lambda cls=cls: cls, name, attr_static))
            elif inspect.isfunction(attr_static) or inspect.ismethoddescriptor(attr_static):
                wrapped = patch_function(attr_static, f"{cls.__name__}.{name}", depth=depth)
                setattr(cls, name, wrapped)
                try:
                    _object_patches.append((weakref.ref(cls), name, attr_static))
                except TypeError:
                    _object_patches.append((lambda cls=cls: cls, name, attr_static))
        except Exception as e:
            logger.error("Error patching %s.%s: %s", cls.__name__, name, e)

# ---------------------
# AI function detection
# ---------------------
def safe_getmembers(module: ModuleType, predicate: Optional[Callable] = None) -> List[Tuple[str, Any]]:
    """Safe version of inspect.getmembers that ignores exceptions during member access."""
    results = []
    try:
        for name in dir(module):
            try:
                obj = getattr(module, name)
                if predicate is None or predicate(obj):
                    results.append((name, obj))
            except (ImportError, AttributeError) as e:
                logger.debug("Skipping member %s due to error: %s", name, e)
    except Exception as e:
        logger.error("Error getting members from module %s: %s", module.__name__, e)
    return results

def auto_patch_ai_functions(
    module_names: Optional[List[str]] = None,
    objects: Optional[List[Any]] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    depth: Optional[int] = None
):
    """Automatically patch AI-related functions safely."""
    include = include or ["forward", "predict", "call", "__call__", "generate", "transform"]
    exclude = exclude or []
    
    # Default modules if none provided
    if module_names is None:
        module_names = [
            "torch.nn", 
            "tensorflow.keras",
            "transformers"
        ]

    # Patch modules
    for mod_name in module_names:
        try:
            module = importlib.import_module(mod_name)
            all_modules = [module]

            # Recursively add submodules using safe_getmembers
            for _, submod in safe_getmembers(module, inspect.ismodule):
                if submod.__name__.startswith(mod_name):
                    all_modules.append(submod)

            for mod in all_modules:
                try:
                    for name in dir(mod):
                        if name in exclude:
                            continue
                        if name not in include:
                            continue
                        
                        try:
                            obj = getattr(mod, name)
                            if callable(obj) and not inspect.isclass(obj):
                                patch_object(mod, name, depth=depth)
                            else:
                                logger.debug("Skipping %s.%s: not callable or is a class", mod.__name__, name)
                        except (ImportError, AttributeError) as e:
                            logger.error("Error patching %s.%s: %s", mod.__name__, name, e)
                except Exception as e:
                    logger.error("Error processing module %s: %s", mod.__name__, e)

        except ImportError:
            logger.warning("Module %s not found, skipping", mod_name)
        except Exception as e:
            logger.error("Error processing module %s: %s", mod_name, e)

    # Patch objects
    if objects:
        for obj in objects:
            if inspect.ismodule(obj):
                # Skip modules since we already handled them
                continue
                
            try:
                obj_name = _resolve_obj_name(obj)
                try:
                    for name in dir(obj):
                        if name in exclude:
                            continue
                        if name not in include:
                            continue
                        
                        try:
                            attr = getattr(obj, name)
                            if callable(attr) and not inspect.isclass(attr):
                                patch_object(obj, name, depth=depth)
                        except (ImportError, AttributeError) as e:
                            logger.error("Error patching object %s attribute %s: %s", obj_name, name, e)
                except Exception as e:
                    logger.error("Error getting dir for object %s: %s", obj_name, e)
            except Exception as e:
                logger.error("Error processing object %s: %s", obj_name, e)

# ---------------------
# Convenience
# ---------------------
# Enhanced plug-and-play patcher
def apply_generic_patches(silent: bool = True, depth: Optional[int] = None, verbose: bool = False):
    """Auto-patch all common AI functions with full detection.
    
    Returns a dict summarizing patched items.
    """
    global _patch_applied
    if _patch_applied:
        return {"status": "already_applied"}

    if not silent:
        logger.info("Applying enhanced generic patches...")

    patched_summary = {
        "modules": {},
        "classes": {},
        "objects": {}
    }

    # Default include/exclude lists
    include = ["forward", "call", "__call__", "predict", "generate", "transform"]
    exclude = []

    # --- 1. Patch common AI modules ---
    module_names = ["torch.nn", "tensorflow.keras", "transformers"]
    for mod_name in module_names:
        try:
            module = importlib.import_module(mod_name)
            for name in dir(module):
                if name in exclude or name not in include:
                    continue
                try:
                    obj = getattr(module, name)
                    if callable(obj) and not inspect.isclass(obj):
                        try:
                            patch_object(module, name, depth=depth)
                            patched_summary["modules"].setdefault(mod_name, []).append(name)
                            if verbose:
                                logger.info("Patched module: %s.%s", mod_name, name)
                        except Exception as e:
                            logger.error("Error patching %s.%s: %s", mod_name, name, e)
                except (ImportError, AttributeError) as e:
                    logger.error("Error accessing %s.%s: %s", mod_name, name, e)
        except ImportError:
            if not silent:
                logger.warning("Module %s not found, skipping.", mod_name)
        except Exception as e:
            logger.error("Error processing module %s: %s", mod_name, e)

    # --- 2. Patch all torch.nn.Module subclasses automatically ---
    if "torch" in sys.modules and torch is not None:
        nn_modules = []
        try:
            for obj_name, obj in globals().items():
                if inspect.isclass(obj):
                    try:
                        if issubclass(obj, torch.nn.Module):
                            nn_modules.append(obj)
                    except (ImportError, TypeError) as e:
                        logger.error("Error checking subclass for %s: %s", obj_name, e)
        except Exception as e:
            logger.error("Error while searching for torch.nn.Module in globals: %s", e)

        # Also include loaded torch modules using safe inspection
        try:
            for name, cls in safe_getmembers(torch.nn, inspect.isclass):
                try:
                    if issubclass(cls, torch.nn.Module):
                        nn_modules.append(cls)
                except (ImportError, TypeError) as e:
                    logger.error("Error checking subclass for %s: %s", name, e)
        except Exception as e:
            logger.error("Error while getting members of torch.nn: %s", e)

        for cls in set(nn_modules):
            try:
                patch_class(cls, exclude=[], skip_dunder=False, depth=depth)
                patched_summary["classes"][cls.__name__] = [m for m in dir(cls) if callable(getattr(cls, m, None))]
                if verbose:
                    logger.info("Patched torch.nn.Module class: %s", cls.__name__)
            except Exception as e:
                logger.error("Error patching class %s: %s", cls.__name__, e)

    # --- 3. Optionally patch custom objects in globals() ---
    for name, obj in globals().items():
        if inspect.isclass(obj) or inspect.ismodule(obj):
            continue
        if hasattr(obj, "__dict__"):
            try:
                for attr_name in dir(obj):
                    if attr_name in exclude or attr_name not in include:
                        continue
                    try:
                        attr = getattr(obj, attr_name)
                        if callable(attr):
                            patch_object(obj, attr_name, depth=depth)
                            patched_summary["objects"].setdefault(type(obj).__name__, []).append(attr_name)
                            if verbose:
                                logger.info("Patched object: %s.%s", type(obj).__name__, attr_name)
                    except (ImportError, AttributeError) as e:
                        logger.error("Error accessing %s.%s: %s", type(obj).__name__, attr_name, e)
            except Exception as e:
                logger.error("Error patching object %s: %s", type(obj).__name__, e)

    _patch_applied = True
    if verbose:
        logger.info("Enhanced generic patching complete.")
    return patched_summary


# Public API
__all__ = [
    "patch_function",
    "patch_object",
    "patch_module",
    "patch_class",
    "apply_generic_patches",
    "safe_serialize",
    "set_log_backend",
    "get_memory_backend",
    "set_max_depth",
    "register_custom_serializer",
    "unpatch_object",
    "unpatch_all",
    "get_and_clear_fallback_logs",
    "auto_patch_ai_functions",
    "LogBackend",
    "MemoryBackend"
]