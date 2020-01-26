from typing import Any, Dict, List, Type

Layer = Dict[str, Any]
Path = List[str]


class TypeMismatchError(ValueError):
    def __init__(self, path: Path, upper_type: Type, lower_type: Type) -> None:
        super().__init__(
            "Entry type mismatch at {!r}, got types {} and {}".format(
                '.'.join(path),
                upper_type.__name__,
                lower_type.__name__,
            ),
        )
        self.path = path
        self.upper_type = upper_type
        self.lower_type = lower_type


def validate_types(path: Path, upper_value: Any, lower_value: Any) -> None:
    if upper_value is lower_value:
        return

    upper_type = type(upper_value)
    lower_type = type(lower_value)

    if upper_type is not lower_type:
        raise TypeMismatchError(path, upper_type, lower_type)


def flatten_pair(upper: Layer, lower: Layer, current_path: Path) -> None:
    for key, value in lower.items():
        key_path = current_path + [key]

        upper_value = upper.setdefault(key, value)

        if upper_value is None:
            # null values in higher layers cause lower layer values
            continue

        validate_types(key_path, upper_value, value)

        if isinstance(value, dict):
            flatten_pair(upper_value, value, key_path)


def flatten(top_layer: Layer, *layers: Layer) -> Layer:
    for layer in layers:
        flatten_pair(top_layer, layer, [])
    return top_layer
