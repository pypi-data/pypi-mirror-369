# aiblackbox/__init__.py
"""
AI BlackBox
Universal & optional framework-specific monkey patching.

Core design:
- Primary focus: generic_patch (universal fallback patcher)
- Optional: framework-specific patches for known AI/ML libs
- Minimal noise on missing integrations
"""

import importlib
import importlib.util
import logging

from .generic_patch import patch_function, patch_object, patch_module
from .blackbox import BlackBox

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Known AI/ML frameworks with their integration patch modules
FRAMEWORK_PATCHES = {
    "openai": "aiblackbox.integrations.patch_openai",
    "torch": "aiblackbox.integrations.patch_pytorch",
    "tensorflow": "aiblackbox.integrations.patch_tensorflow",
    "sklearn": "aiblackbox.integrations.patch_sklearn",
    "transformers": "aiblackbox.integrations.patch_transformers",
    "langchain": "aiblackbox.integrations.patch_langchain",
}


# ---------------------------
# Helpers
# ---------------------------

def is_package_installed(package_name: str) -> bool:
    """Check if a package is installed in the environment."""
    return importlib.util.find_spec(package_name) is not None


# ---------------------------
# Patching functions
# ---------------------------

def apply_framework_patches(silent: bool = True) -> bool:
    """
    Attempt to apply framework-specific patches.
    Returns True if at least one patch was applied.
    """
    patched_any = False
    for framework, patch_module_path in FRAMEWORK_PATCHES.items():
        if not is_package_installed(framework):
            continue

        try:
            patch_module = importlib.import_module(patch_module_path)
            if hasattr(patch_module, "apply_patches"):
                patch_module.apply_patches()
                logger.info(f"[AI BlackBox] Patched framework: {framework}")
                patched_any = True
            elif not silent:
                logger.warning(f"[AI BlackBox] No 'apply_patches()' in {patch_module_path}")
        except Exception as e:
            if not silent:
                logger.warning(f"[AI BlackBox] Could not patch {framework}: {e}")

    return patched_any


def apply_generic_patch(silent: bool = True):
    """
    Apply generic fallback patching to all compatible targets.
    """
    try:
        from .generic_patch import apply_generic_patches
        apply_generic_patches()
        logger.info("[AI BlackBox] Applied generic universal patches")
    except Exception as e:
        if not silent:
            logger.error(f"[AI BlackBox] Generic patch failed: {e}")


def apply_all_patches(priority: str = "generic", silent: bool = True):
    """
    Apply patches in chosen priority order:
    - priority='generic': generic first, then frameworks
    - priority='framework': frameworks first, then generic
    """
    if priority == "generic":
        apply_generic_patch(silent=silent)
        apply_framework_patches(silent=silent)
    elif priority == "framework":
        patched = apply_framework_patches(silent=silent)
        if not patched:
            apply_generic_patch(silent=silent)
    else:
        raise ValueError("priority must be 'generic' or 'framework'")


# ---------------------------
# Auto-run control
# ---------------------------

AUTO_PATCH_ON_IMPORT = False  # Set to True if you want auto-patching on import

if __name__ != "__main__" and AUTO_PATCH_ON_IMPORT:
    apply_all_patches(priority="generic", silent=True)


# ---------------------------
# Public API
# ---------------------------

__all__ = [
    "BlackBox",
    "patch_function",
    "patch_object",
    "patch_module",
    "apply_generic_patch",
    "apply_framework_patches",
    "apply_all_patches",
]
