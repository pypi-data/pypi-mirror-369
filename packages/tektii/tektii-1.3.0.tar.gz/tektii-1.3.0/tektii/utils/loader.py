"""Strategy loading utilities."""

import importlib.util
from typing import Type

from tektii.strategy import TektiiStrategy


def load_strategy_class(module_path: str, class_name: str) -> Type[TektiiStrategy]:
    """Load a strategy class from a module file.

    Args:
        module_path: Path to Python module containing the strategy
        class_name: Name of the strategy class to load

    Returns:
        The strategy class

    Raises:
        Exception: If loading fails
    """
    spec = importlib.util.spec_from_file_location("strategy", module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, class_name):
        raise ValueError(f"Module does not contain class {class_name}")

    strategy_class = getattr(module, class_name)

    if not issubclass(strategy_class, TektiiStrategy):
        raise ValueError(f"{class_name} is not a subclass of TektiiStrategy")

    return strategy_class  # type: ignore[no-any-return]
