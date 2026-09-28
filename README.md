# STUDY-PLANNER-WITH-SPACED-REPITITION

# 🧠 Study Planner (Exam-Aware SM-2 Scheduler)

A lightweight, zero-dependency command-line spaced repetition tool designed specifically for students. 

Unlike traditional SM-2 flashcard apps, this planner is **exam-aware**. It dynamically compresses review intervals as your exam date approaches and automatically ensures your final review lands the day before the test. 

## ✨ Features

- **Spaced Repetition (SM-2):** Adapts to your memory. Hard topics appear more frequently; easy topics are spaced out.
- **Exam Awareness:** Define an exam date and the algorithm will cap intervals so you don't miss a review before the big day.
- **Zero Dependencies:** Written purely in Python Standard Library (Python 3.8+).
- **Local Storage:** All your data lives locally in a single, easily readable `planner_data.json` file.
- **Fast CLI:** Add topics, review due items, and check your upcoming schedule straight from the terminal.

## 🚀 Installation

Since it uses only the standard library, no `pip install` is required. Just clone the repository and run the script:

```bash
git clone [https://github.com/yourusername/study-planner.git](https://github.com/yourusername/study-planner.git)
cd study-planner
python study_planner.py --help
