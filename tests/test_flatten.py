import unittest

from layer_loader import flatten, types


class TestFlatten(unittest.TestCase):
    def test_single_layer(self) -> None:
        layer = {'a': 1, 'b': 2}  # type: types.Layer
        result = flatten.flatten(layer)
        self.assertEqual({'a': 1, 'b': 2}, result)

    def test_distinct_layers(self) -> None:
        layer_1 = {'a': 1}  # type: types.Layer
        layer_2 = {'b': 2}  # type: types.Layer
        layer_3 = {'c': 3}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2, layer_3)
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, result)

    def test_overlapping_scalar(self) -> None:
        layer_1 = {'a': 1, 'b': 2}  # type: types.Layer
        layer_2 = {'b': 42}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2)
        self.assertEqual({'a': 1, 'b': 2}, result)

    def test_overlapping_list(self) -> None:
        layer_1 = {'a': 1, 'b': [2]}  # type: types.Layer
        layer_2 = {'b': [42]}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2)
        self.assertEqual({'a': 1, 'b': [2]}, result)

    def test_overlapping_shallow_nested(self) -> None:
        layer_1 = {'a': {'b': {'X': 4}}}  # type: types.Layer
        layer_2 = {'a': {'c': {'Y': 5}}}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2)
        self.assertEqual(
            {'a': {
                'b': {'X': 4},
                'c': {'Y': 5},
            }},
            result,
        )

    def test_overlapping_deep_nested(self) -> None:
        layer_1 = {'a': {'b': {'c': 4}}}  # type: types.Layer
        layer_2 = {'a': {'b': {'d': 5}}}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2)
        self.assertEqual(
            {'a': {'b': {'c': 4, 'd': 5}}},
            result,
        )

    def test_null_removes_entry(self) -> None:
        layer_1 = {'a': {'b': None}}  # type: types.Layer
        layer_2 = {'a': {'b': {'X': 1}, 'c': {'Y': 2}}}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2)
        self.assertEqual(
            {'a': {'b': None, 'c': {'Y': 2}}},
            result,
        )

    def test_null_removes_entry_when_further_overridden(self) -> None:
        layer_1 = {'a': {'b': {'Z': 1}}}  # type: types.Layer
        layer_2 = {'a': {'b': None}}  # type: types.Layer
        layer_3 = {'a': {'b': {'X': 1}, 'c': {'Y': 2}}}  # type: types.Layer
        result = flatten.flatten(layer_1, layer_2, layer_3)
        self.assertEqual(
            {'a': {'b': {'Z': 1}, 'c': {'Y': 2}}},
            result,
        )

    def test_different_types_is_error(self) -> None:
        layer_1 = {'a': 'a'}  # type: types.Layer
        layer_2 = {'a': 1}  # type: types.Layer

        with self.assertRaises(flatten.TypeMismatchError) as cm:
            flatten.flatten(layer_1, layer_2)

        self.assertEqual(
            "Entry type mismatch at 'a', got types str and int",
            str(cm.exception),
        )
