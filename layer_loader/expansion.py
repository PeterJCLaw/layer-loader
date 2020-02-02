import collections
import re
from typing import Dict, List, Match, Tuple, cast

from .types import Layer, LayerElement, Path

PLACEHOLDER = re.compile(r'{([\w\.]+)}')

VALID_TYPES = (float, int, str)


class PlaceholderMissingError(ValueError):
    def __init__(self, placeholder: Path, progress: Path, context: Path) -> None:
        super().__init__(
            "Placeholder {!r} (from {}) could not be expanded beyond {!r}".format(
                '.'.join(placeholder),
                '.'.join(context),
                '.'.join(progress),
            ),
        )
        self.placeholder = placeholder
        self.progress = progress
        self.context = context


class CyclicPlaceholderError(ValueError):
    def __init__(self, placeholders: List[Path]) -> None:
        super().__init__(
            "Cyclic placeholder found: {}".format(
                ' -> '.join('.'.join(x) for x in (*placeholders, placeholders[0])),
            ),
        )
        self.placeholders = placeholders


class InvalidPlaceholderTypeError(TypeError):
    def __init__(self, value: LayerElement, path: Path) -> None:
        super().__init__(
            "Value {!r} at {!r} is not a valid placeholder type".format(
                value,
                '.'.join(path),
            ),
        )
        self.value = value
        self.path = path


def lookup(layer: Layer, path: Path, context: Path) -> str:
    mapping = layer

    last_idx = len(path) - 1

    for idx, part in enumerate(path):
        try:
            element = mapping[part]
        except KeyError:
            raise PlaceholderMissingError(path, path[:idx], context)

        if idx != last_idx:
            if not isinstance(element, dict):
                raise PlaceholderMissingError(path, path[:idx + 1], context)
            else:
                mapping = element

    # Note: can't use isinstance since `bool` is a subtype of `int`, yet we
    # don't want to allow bools but do want to allow `int`s.
    if type(element) not in VALID_TYPES:
        raise InvalidPlaceholderTypeError(element, path)

    return str(element)


PLACEHOLDER_STACK = collections.OrderedDict()  # type: Dict[Tuple[str, ...], None]


def do_expansion(root: Layer, value: LayerElement, key_path: Path) -> LayerElement:
    def repl(match: Match) -> str:
        placeholder_str = match.group(1)
        path = placeholder_str.split('.')
        path_tuple = tuple(path)

        if path_tuple in PLACEHOLDER_STACK:
            raise CyclicPlaceholderError(
                [list(x) for x in PLACEHOLDER_STACK.keys()],
            )

        PLACEHOLDER_STACK[path_tuple] = None
        try:
            new_value = lookup(root, path, key_path)
            expanded = do_expansion(root, new_value, path)
            # Need to cast because logically `do_expansion` will actually always
            # return the same type as that of the `value` it is given, however
            # accurately representing that using Python's type system ends up
            # needing casts in each of the isinstance guarded `return`s below.
            # Having the cast here is therefore simpler.
            # See https://github.com/python/mypy/issues/8354 for details.
            return cast(str, expanded)
        finally:
            del PLACEHOLDER_STACK[path_tuple]

    if isinstance(value, str):
        return PLACEHOLDER.sub(repl, value)

    elif isinstance(value, list):
        return [
            do_expansion(root, x, key_path + [str(idx)])
            for idx, x in enumerate(value)
        ]

    elif isinstance(value, dict):
        return _expand(root, value, key_path)

    return value


def _expand(root: Layer, part: Layer, current_path: Path) -> Layer:
    for key, value in part.items():
        key_path = current_path + [key]
        part[key] = do_expansion(root, value, key_path)

    return part


def expand(layer: Layer) -> Layer:
    return _expand(layer, layer, [])
