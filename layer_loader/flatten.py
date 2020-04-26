from typing import Type

from .types import Layer, LayerElement, Path


class TypeMismatchError(ValueError):
    def __init__(
        self,
        path: Path,
        upper_type: Type[object],
        lower_type: Type[object],
    ) -> None:
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


def validate_types(
    path: Path,
    upper_value: LayerElement,
    lower_value: LayerElement,
) -> None:
    upper_type = type(upper_value)
    lower_type = type(lower_value)

    if upper_type is not lower_type:
        raise TypeMismatchError(path, upper_type, lower_type)


def flatten_pair(upper: Layer, lower: Layer, current_path: Path) -> None:
    for key, value in lower.items():
        key_path = current_path + [key]

        upper_value = upper.setdefault(key, value)

        if upper_value is value:
            # optimisation to prevent recursing into nested mappings where
            # nothing will change
            continue

        if None in (upper_value, value):
            # explicit nulls are allowed in order to clear lower values
            continue

        validate_types(key_path, upper_value, value)

        if isinstance(value, dict):
            assert isinstance(upper_value, dict)
            flatten_pair(upper_value, value, key_path)


def flatten(top_layer: Layer, *layers: Layer) -> Layer:
    layers = tuple(reversed([top_layer, *layers]))

    for upper, lower in zip(layers[1:], layers):
        flatten_pair(upper, lower, [])
    return top_layer
