import unittest
from datetime import date
from src.scheduler import schedule, due_topics, is_active

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 9, 28)
        self.base_topic = {
            "id": 1,
            "name": "Graphs",
            "subject": "DSA",
            "exam": None,
            "ease": 2.5,
            "interval": 0,
            "reps": 0,
            "next_review": self.today.isoformat(),
            "history": []
        }

    def test_failed_recall_resets_interval(self):
        """A score < 3 should set interval to 1 and reps to 0."""
        self.base_topic["reps"] = 5
        self.base_topic["interval"] = 15
        schedule(self.base_topic, 2, self.today)
        self.assertEqual(self.base_topic["reps"], 0)
        self.assertEqual(self.base_topic["interval"], 1)

    def test_exam_compression(self):
        """Topic interval should cap at half the days remaining until exam."""
        self.base_topic["exam"] = "2026-10-08" # 10 days away
        self.base_topic["reps"] = 3
        self.base_topic["interval"] = 14 # Algorithm would normally want 14 days
        schedule(self.base_topic, 4, self.today)
        
        # Should cap at 10 // 2 = 5 days
        self.assertEqual(self.base_topic["interval"], 5)
        self.assertEqual(self.base_topic["next_review"], "2026-10-03")

    def test_final_review_before_exam(self):
        """Ensures the last review falls exactly the day before the exam."""
        self.base_topic["exam"] = "2026-9-30" # 2 days away
        schedule(self.base_topic, 4, self.today)
        # Force sets next_review to day before the exam (2026-09-29)
        self.assertEqual(self.base_topic["next_review"], "2026-09-29")

    def test_due_topics(self):
        """Tests that overdue and due topics are returned, but not future ones."""
        db = {"topics": [
            {**self.base_topic, "id": 1, "next_review": "2026-09-27"}, # Overdue
            {**self.base_topic, "id": 2, "next_review": "2026-09-28"}, # Today
            {**self.base_topic, "id": 3, "next_review": "2026-09-29"}, # Future
        ]}
        due = due_topics(db, self.today)
        self.assertEqual(len(due), 2)
        self.assertEqual(due[0]["id"], 1) # Checks sorting (overdue first)
