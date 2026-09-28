"""
Study Planner with Spaced Repetition
------------------------------------
An exam-aware SM-2 scheduler. Standard library only (Python 3.8+).
 
Usage:
  python study_planner.py add "Linked Lists" --subject DSA --exam 2026-12-10
  python study_planner.py today            # what to revise today
  python study_planner.py review           # rate each due topic (0-5)
  python study_planner.py plan --days 7    # upcoming schedule
  python study_planner.py list             # all topics
  python study_planner.py delete 3         # remove topic by id
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path
 
DB_FILE = Path(__file__).with_name("planner_data.json")
MIN_EASE = 1.3
 
 
# ---------- storage ----------
def load():
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text())
    return {"next_id": 1, "topics": []}
 
 
def save(db):
    DB_FILE.write_text(json.dumps(db, indent=2))
 
 
def parse_date(s):
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise SystemExit(f"Invalid date '{s}'. Use YYYY-MM-DD.")
 
 
# ---------- scheduling core ----------
def schedule(topic, quality, today):
    """Update a topic after a review. quality: 0 (blackout) .. 5 (perfect)."""
    if quality < 3:                      # failed recall -> start over, see tomorrow
        topic["reps"] = 0
        topic["interval"] = 1
    else:
        topic["reps"] += 1
        if topic["reps"] == 1:
            topic["interval"] = 1
        elif topic["reps"] == 2:
            topic["interval"] = 3        # shorter than SM-2's 6 days: fits exam prep
        else:
            topic["interval"] = round(topic["interval"] * topic["ease"])
 
    # SM-2 ease-factor update
    topic["ease"] = max(
        MIN_EASE,
        topic["ease"] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02),
    )
 
    # Exam awareness: compress intervals as the exam approaches, and make
    # sure the last review lands the day before the exam.
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
 
 
def is_active(topic, today):
    exam = topic.get("exam")
    return not exam or date.fromisoformat(exam) >= today
 
 
def due_topics(db, today):
    due = [
        t for t in db["topics"]
        if is_active(t, today) and date.fromisoformat(t["next_review"]) <= today
    ]
    # most urgent first: nearest exam, then most overdue
    due.sort(key=lambda t: (t.get("exam") or "9999-12-31", t["next_review"]))
    return due
 
 
# ---------- commands ----------
def cmd_add(args, db):
    today = date.today()
    exam = parse_date(args.exam) if args.exam else None
    if exam and exam < today:
        raise SystemExit("Exam date is in the past.")
    topic = {
        "id": db["next_id"],
        "name": args.name,
        "subject": args.subject or "General",
        "exam": exam.isoformat() if exam else None,
        "ease": 2.5,
        "interval": 0,
        "reps": 0,
        "next_review": today.isoformat(),   # first study session is today
        "history": [],
    }
    db["next_id"] += 1
    db["topics"].append(topic)
    save(db)
    print(f"Added #{topic['id']}: {topic['name']} [{topic['subject']}]"
          + (f" (exam {topic['exam']})" if exam else ""))
 
 
def fmt_topic(t, today):
    exam = t.get("exam")
    tag = ""
    if exam:
        tag = f" | exam in {(date.fromisoformat(exam) - today).days}d"
    return f"#{t['id']:<3} {t['name']} [{t['subject']}]{tag}"
 
 
def cmd_today(args, db):
    today = date.today()
    due = due_topics(db, today)
    if not due:
        print("Nothing due today. 🎉")
        return
    print(f"Due today ({today}): {len(due)} topic(s)\n")
    for t in due:
        overdue = (today - date.fromisoformat(t["next_review"])).days
        late = f"  (overdue {overdue}d)" if overdue > 0 else ""
        print("  " + fmt_topic(t, today) + late)
 
 
def cmd_review(args, db):
    today = date.today()
    due = due_topics(db, today)
    if not due:
        print("Nothing to review today.")
        return
    print("Rate recall: 0 = blank, 3 = hard but got it, 5 = perfect. (q to quit)\n")
    for t in due:
        while True:
            ans = input(f"{fmt_topic(t, today)}\n  Rating (0-5): ").strip().lower()
            if ans == "q":
                save(db)
                return
            if ans.isdigit() and 0 <= int(ans) <= 5:
                break
            print("  Enter a number 0-5.")
        schedule(t, int(ans), today)
        print(f"  -> next review {t['next_review']} (interval {t['interval']}d)\n")
    save(db)
    print("All done for today.")
 
 
def cmd_plan(args, db):
    today = date.today()
    print(f"Schedule for the next {args.days} days\n")
    for offset in range(args.days):
        day = today + timedelta(days=offset)
        items = [
            t for t in db["topics"]
            if is_active(t, day) and (
                date.fromisoformat(t["next_review"]) == day
                or (offset == 0 and date.fromisoformat(t["next_review"]) < day)
            )
        ]
        label = day.strftime("%a %d %b")
        print(f"{label}: " + (", ".join(t["name"] for t in items) if items else "-"))
    print("\nNote: future days only show each topic's *next* review; later "
          "ones depend on your ratings.")
 
 
def cmd_list(args, db):
    today = date.today()
    if not db["topics"]:
        print("No topics yet. Add one with: add \"Topic\" --exam YYYY-MM-DD")
        return
    for t in sorted(db["topics"], key=lambda x: x["next_review"]):
        status = "" if is_active(t, today) else "  [exam passed]"
        print(f"{fmt_topic(t, today)} | next {t['next_review']} | "
              f"reps {t['reps']} | ease {t['ease']:.2f}{status}")
 
 
def cmd_delete(args, db):
    before = len(db["topics"])
    db["topics"] = [t for t in db["topics"] if t["id"] != args.id]
    if len(db["topics"]) == before:
        raise SystemExit(f"No topic with id {args.id}.")
    save(db)
    print(f"Deleted #{args.id}.")
 
 
# ---------- CLI ----------
def main():
    p = argparse.ArgumentParser(description="Spaced-repetition study planner")
    sub = p.add_subparsers(dest="cmd", required=True)
 
    a = sub.add_parser("add", help="add a topic")
    a.add_argument("name")
    a.add_argument("--subject", "-s")
    a.add_argument("--exam", "-e", help="exam date, YYYY-MM-DD")
    a.set_defaults(fn=cmd_add)
 
    sub.add_parser("today", help="topics due today").set_defaults(fn=cmd_today)
    sub.add_parser("review", help="review due topics").set_defaults(fn=cmd_review)
 
    pl = sub.add_parser("plan", help="upcoming schedule")
    pl.add_argument("--days", "-d", type=int, default=7)
    pl.set_defaults(fn=cmd_plan)
 
    sub.add_parser("list", help="list all topics").set_defaults(fn=cmd_list)
 
    d = sub.add_parser("delete", help="delete a topic")
    d.add_argument("id", type=int)
    d.set_defaults(fn=cmd_delete)
 
    args = p.parse_args()
    args.fn(args, load())
 
 
if __name__ == "__main__":
    main()
