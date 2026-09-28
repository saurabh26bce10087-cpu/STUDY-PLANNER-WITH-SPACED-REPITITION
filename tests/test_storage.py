import unittest
import tempfile
import json
from pathlib import Path
from src.storage import load, save

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.test_dir.name) / "test_db.json"
        self.dummy_data = {"next_id": 2, "topics": [{"id": 1, "name": "Test"}]}

    def tearDown(self):
        self.test_dir.cleanup()

    def test_load_empty(self):
        db = load(self.db_path)
        self.assertEqual(db["next_id"], 1)
        self.assertEqual(db["topics"], [])

    def test_save_and_load(self):
        save(self.dummy_data, self.db_path)
        self.assertTrue(self.db_path.exists())
        
        loaded = load(self.db_path)
        self.assertEqual(loaded["next_id"], 2)
        self.assertEqual(loaded["topics"][0]["name"], "Test")
