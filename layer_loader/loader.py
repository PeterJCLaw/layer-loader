import contextlib
from pathlib import Path
from typing import IO, Any, Callable, Iterable, Union, cast

from . import expansion, flatten, types


class InvalidLayerError(ValueError):
    def __init__(self, source: IO[str], layer_number: int) -> None:
        try:
            name = "File {}".format(source.name)
        except AttributeError:
            name = "{} at layer {}".format(type(source).__name__, layer_number)

        super().__init__(
            "{} has invalid content -- root element must be a mapping".format(
                name,
            ),
        )
        self.source = source
        self.layer_number = layer_number


def validated_load(
    source: Union[str, Path, IO[str]],
    loader: Callable[[IO[str]], Any],
    layer_number: int,
) -> types.Layer:
    with contextlib.ExitStack() as stack:
        if isinstance(source, str):
            source = open(source)
            stack.enter_context(source)

        elif isinstance(source, Path):
            source = source.open()
            stack.enter_context(source)

        data = loader(source)

        if not isinstance(data, dict):
            raise InvalidLayerError(source, layer_number)

    # As checked by isinstance
    return cast(types.Layer, data)


def load_files(
    files: Iterable[Union[str, Path, IO[str]]],
    loader: Callable[[IO[str]], Any],
) -> types.Layer:
    layers = [validated_load(x, loader, idx) for idx, x in enumerate(files)]

    if not layers:
        raise ValueError("Must provide at least one layer file")

    root = flatten.flatten(layers[0], *layers[1:])
    return expansion.expand(root)
