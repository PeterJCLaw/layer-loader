import collections
import unittest

from layer_loader import expansion, types


class TestExpansion(unittest.TestCase):
    def test_ignores_keys(self) -> None:
        data = {'foo {place.holder} bar': 4}  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual({'foo {place.holder} bar': 4}, expanded)

    def test_expands_placeholders_in_values(self) -> None:
        data = {
            'a': 'foo {place_holder} bar',
            'place_holder': '99',
        }  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual(
            {
                'a': 'foo 99 bar',
                'place_holder': '99',
            },
            expanded,
        )

    def test_expands_placeholders_in_nested_values(self) -> None:
        data = {
            'a': {'b': 'foo {place_holder} bar'},
            'place_holder': '99',
        }  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual(
            {
                'a': {'b': 'foo 99 bar'},
                'place_holder': '99',
            },
            expanded,
        )

    def test_expands_placeholders_in_values_in_lists(self) -> None:
        data = {
            'a': {'b': ['foo {place_holder} bar']},
            'place_holder': '99',
        }  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual(
            {
                'a': {'b': ['foo 99 bar']},
                'place_holder': '99',
            },
            expanded,
        )

    def test_expands_dotted_placeholders(self) -> None:
        data = {
            'a': 'foo {place.holder} bar',
            'place': {'holder': '99'},
        }  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual(
            {
                'a': 'foo 99 bar',
                'place': {'holder': '99'},
            },
            expanded,
        )

    def test_expands_all_placeholders(self) -> None:
        data = {
            'a': 'foo {place_holder} {place_holder_2} {place_holder} bar',
            'place_holder': '99',
            'place_holder_2': '22',
        }  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual(
            {
                'a': 'foo 99 22 99 bar',
                'place_holder': '99',
                'place_holder_2': '22',
            },
            expanded,
        )

    def test_expands_placeholders_recursively(self) -> None:
        data = {
            'a': 'foo {place_holder_1} {place_holder_2} {place_holder_3} bar',
            'place_holder_1': '11',
            'place_holder_2': '{place_holder_1}',
            'place_holder_3': '{place_holder_2}',
        }  # type: types.Layer
        expanded = expansion.expand(data)
        self.assertEqual(
            {
                'a': 'foo 11 11 11 bar',
                'place_holder_1': '11',
                'place_holder_2': '11',
                'place_holder_3': '11',
            },
            expanded,
        )

    def test_errors_on_cyclic_placeholders(self) -> None:
        # OrderedDict for predictable cycle ordering
        data = collections.OrderedDict([
            ('a', 'foo {place_holder_1} bar'),
            ('place_holder_1', '{place_holder_3}'),
            ('place_holder_2', '{place_holder_1}'),
            ('place_holder_3', '{place_holder_2}'),
        ])  # type: types.Layer

        with self.assertRaises(expansion.CyclicPlaceholderError) as cm:
            expansion.expand(data)

        self.assertEqual(
            [['place_holder_1'], ['place_holder_3'], ['place_holder_2']],
            cm.exception.placeholders,
        )

    def test_errors_on_missing_placeholder(self) -> None:
        data = {
            'a': 'foo {place_holder} bar',
        }  # type: types.Layer

        with self.assertRaises(expansion.PlaceholderMissingError) as cm:
            expansion.expand(data)

        self.assertEqual(
            ['place_holder'],
            cm.exception.placeholder,
        )

        self.assertEqual(
            [],
            cm.exception.progress,
        )

        self.assertEqual(
            ['a'],
            cm.exception.context,
        )

    def test_errors_on_missing_nested_placeholder(self) -> None:
        data = {
            'a': 'foo {place.holder} bar',
            'place': {'a': None},
        }  # type: types.Layer

        with self.assertRaises(expansion.PlaceholderMissingError) as cm:
            expansion.expand(data)

        self.assertEqual(
            ['place', 'holder'],
            cm.exception.placeholder,
        )

        self.assertEqual(
            ['place'],
            cm.exception.progress,
        )

        self.assertEqual(
            ['a'],
            cm.exception.context,
        )

    def test_errors_on_invalid_placeholder_values(self) -> None:
        for invalid_value in (
            True,
            None,
            ['a'],
            {'a': None},
        ):
            with self.subTest(invalid_value=invalid_value):
                data = {
                    'a': 'foo {place_holder} bar',
                    'place_holder': invalid_value,
                }  # type: types.Layer
                with self.assertRaises(expansion.InvalidPlaceholderTypeError):
                    expansion.expand(data)
