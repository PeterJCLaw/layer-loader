import json
import os.path
import subprocess
import sys
import unittest
from pathlib import Path

import layer_loader

MY_DIR = os.path.dirname(os.path.abspath(__file__))


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

        data = layer_loader.load_files(
            [
                self.data_path('overlay.json'),
                Path(self.data_path('base.json')),
            ],
            loader=json.load,
        )

        self.assertEqual(expected, data)

    def test_run_module(self) -> None:
        expected = {
            "a": 1,
            "endpoints": [
                "http://localhost:8000/abc",
                "http://localhost:8000/def",
                "http://localhost:8000/ghi",
            ],
            "url": "http://localhost:8000",
        }

        output = subprocess.check_output([
            sys.executable,
            '-m', 'layer_loader',
            '--loader=json.load',
            'tests/data/overlay.json',
            'tests/data/a.json',
            'tests/data/base.json',
        ]).decode('utf-8')

        data = json.loads(output)

        self.assertEqual(expected, data)
