from typing import Any, Dict, List, Union

LayerElement = Union[bool, float, int, str, None, List[Any], Dict[str, Any]]
Layer = Dict[str, LayerElement]
Path = List[str]
