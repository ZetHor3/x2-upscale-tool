"""Compatibility fixes for third-party packages."""


def patch_basicsr():
    """Patch basicsr for torchvision >= 0.21 compatibility.

    basicsr imports `torchvision.transforms.functional_tensor` which was
    removed in torchvision 0.21+. We alias it to v2.functional.
    """
    import sys

    if "torchvision.transforms.functional_tensor" in sys.modules:
        return  # already patched

    try:
        import torchvision.transforms.v2.functional as Fv2
        import torchvision.transforms.functional as F

        # Create a proxy module
        import types
        mod = types.ModuleType("torchvision.transforms.functional_tensor")
        mod.rgb_to_grayscale = Fv2.rgb_to_grayscale

        # Copy other functions that basicsr might use
        for name in dir(Fv2):
            if name.startswith("_") or hasattr(mod, name):
                continue
            setattr(mod, name, getattr(Fv2, name, None))

        sys.modules["torchvision.transforms.functional_tensor"] = mod
    except ImportError:
        pass  # torchvision not installed, nothing to patch
