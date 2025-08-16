from __future__ import annotations

from typing import Literal


def list_model_organisms() -> list[str]:
    """List the model organisms located in the /models directory."""
    return _list_objects("models")


def list_detectors() -> list[str]:
    """List the detectors located in the /detectors directory."""
    return _list_objects("detectors")


def list_environments() -> list[str]:
    """List the environments located in the /environments directory."""
    return _list_objects("environments")


def list_configs() -> list[str]:
    """List the configs located in the /configs directory."""
    return _list_objects("configs")


CATEGORY_TO_OBJECT_TYPE = {
    "models": "ModelOrganism",
    "detectors": "Detector",
    "environments": "Environment",
}


def _list_objects(
    category: Literal["models", "detectors", "environments", "configs"],
) -> list[str]:
    """List the objects in the specified category. The objects are stored in the appropriate directories and are named main.py"""
    import os
    from .root_location import get_bench_af_root

    root = get_bench_af_root()
    if not os.path.exists(root / category):
        return []
    
    if category == "configs":
        return os.listdir(root / category)

    objects = []
    # Traverse the subdirectories of the category directory
    for subdir in os.listdir(root / category):
        if os.path.isdir(root / category / subdir):
            # Check if there is a main.py file in the subdirectory
            main_file = root / category / subdir / "main.py"
            # Check that there is a get() function in the main.py file
            if os.path.exists(main_file):
                with open(main_file) as f:
                    code = f.read()
                    if f"def get() -> {CATEGORY_TO_OBJECT_TYPE[category]}:" in code:
                        objects.append(subdir)
                    else:
                        print(
                            f"Issue with {category}/{subdir}/main.py: There should be a get() function that returns a {CATEGORY_TO_OBJECT_TYPE[category]} object"
                        )
    return objects
