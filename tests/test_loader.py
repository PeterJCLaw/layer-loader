import io
import json
import os.path
import unittest
from pathlib import Path
from typing import IO, cast
from unittest import mock

from layer_loader import loader

MY_DIR = os.path.dirname(os.path.abspath(__file__))


def mock_open_a_json(read_data: str = '{"a": 1}') -> IO[str]:
    mock_fileobj = mock.MagicMock(name='a.json')
    return cast(
        IO[str],
        mock.mock_open(mock_fileobj, read_data),
    )


class TestLoader(unittest.TestCase):
    def data_path(self, file_name: str) -> str:
        return os.path.join(MY_DIR, 'data', file_name)

    def test_loads_json_files(self) -> None:
        expected = {
            "endpoints": [
                "http://localhost:8000/abc",
                "http://localhost:8000/def",
                "http://localhost:8000/ghi",
            ],
            "url": "http://localhost:8000",
        }

        data = loader.load_files(
            [self.data_path('overlay.json'), self.data_path('base.json')],
            loader=json.load,
        )

        self.assertEqual(expected, data)

    @mock.patch('layer_loader.loader.open', mock_open_a_json())
    def test_filenames_as_strings(self) -> None:
        data = loader.load_files(['a.json'], loader=json.load)
        self.assertEqual({'a': 1}, data)

    @mock.patch('io.open', mock_open_a_json())
    def test_filenames_as_paths(self) -> None:
        data = loader.load_files([Path('a.json')], loader=json.load)
        self.assertEqual({'a': 1}, data)

    def test_file_object(self) -> None:
        with open(self.data_path('a.json')) as f:
            data = loader.load_files([f], loader=json.load)

        self.assertEqual({'a': 1}, data)

    def test_string_io(self) -> None:
        fileobj = io.StringIO('{"a": 1}')
        data = loader.load_files([fileobj], loader=json.load)
        self.assertEqual({'a': 1}, data)

    def test_rejects_non_mapping_root(self) -> None:
        with mock.patch('layer_loader.loader.open', mock_open_a_json(read_data='42')):
            with self.assertRaises(loader.InvalidLayerError) as cm:
                loader.load_files(['a.json'], loader=json.load)

        self.assertIn('a.json', str(cm.exception))

    def test_rejects_non_mapping_root_string_io(self) -> None:
        # StringIO doesn't have `.name`, which most other file objects do.
        fileobj = io.StringIO('42')

        with self.assertRaises(loader.InvalidLayerError) as cm:
            loader.load_files([fileobj], loader=json.load)

        self.assertIn('StringIO at layer 0', str(cm.exception))
