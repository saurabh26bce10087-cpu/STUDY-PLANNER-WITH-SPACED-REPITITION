from datetime import date, timedelta

MIN_EASE = 1.3

def schedule(topic: dict, quality: int, today: date):
    """Update a topic after a review. quality: 0 (blackout) .. 5 (perfect)."""
    if quality < 3:
        topic["reps"] = 0
        topic["interval"] = 1
    else:
        topic["reps"] += 1
        if topic["reps"] == 1:
            topic["interval"] = 1
        elif topic["reps"] == 2:
            topic["interval"] = 3
        else:
            topic["interval"] = round(topic["interval"] * topic["ease"])

    topic["ease"] = max(
        MIN_EASE,
        topic["ease"] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02),
    )

    exam = topic.get("exam")
    if exam:
        days_left = (date.fromisoformat(exam) - today).days
        topic["interval"] = max(1, min(topic["interval"], days_left // 2))
        nxt = today + timedelta(days=topic["interval"])
        last_day = date.fromisoformat(exam) - timedelta(days=1)
        if nxt > last_day:
            nxt = max(today + timedelta(days=1), last_day)
    else:
        nxt = today + timedelta(days=topic["interval"])

    topic["next_review"] = nxt.isoformat()
    topic["history"].append({"date": today.isoformat(), "quality": quality})

def is_active(topic: dict, today: date) -> bool:
    exam = topic.get("exam")
    return not exam or date.fromisoformat(exam) >= today

def due_topics(db: dict, today: date) -> list:
    due = [
        t for t in db["topics"]
        if is_active(t, today) and date.fromisoformat(t["next_review"]) <= today
    ]
    due.sort(key=lambda t: (t.get("exam") or "9999-12-31", t["next_review"]))
    return due
