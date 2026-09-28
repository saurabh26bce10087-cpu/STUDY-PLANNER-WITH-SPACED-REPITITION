import argparse
from datetime import date, timedelta
from src.storage import parse_date, save
from src.scheduler import schedule, is_active, due_topics

def fmt_topic(t, today):
    exam = t.get("exam")
    tag = f" | exam in {(date.fromisoformat(exam) - today).days}d" if exam else ""
    return f"#{t['id']:<3} {t['name']} [{t['subject']}]{tag}"

def cmd_add(args, db, db_path):
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
        "next_review": today.isoformat(),
        "history": [],
    }
    db["next_id"] += 1
    db["topics"].append(topic)
    save(db, db_path)
    print(f"Added #{topic['id']}: {topic['name']} [{topic['subject']}]")

def cmd_today(args, db, db_path):
    today = date.today()
    due = due_topics(db, today)
    if not due:
        print("Nothing due today. 🎉")
        return
    print(f"Due today ({today}): {len(due)} topic(s)\n")
    for t in due:
        print("  " + fmt_topic(t, today))

def cmd_review(args, db, db_path):
    today = date.today()
    due = due_topics(db, today)
    if not due:
        print("Nothing to review today.")
        return
    
    for t in due:
        while True:
            ans = input(f"{fmt_topic(t, today)}\n  Rating (0-5, q to quit): ").strip().lower()
            if ans == "q":
                save(db, db_path)
                return
            if ans.isdigit() and 0 <= int(ans) <= 5:
                break
            print("  Enter a number 0-5.")
        schedule(t, int(ans), today)
        print(f"  -> next review {t['next_review']} (interval {t['interval']}d)\n")
    save(db, db_path)
    print("All done for today.")

def cmd_plan(args, db, db_path):
    today = date.today()
    print(f"Schedule for the next {args.days} days\n")
    for offset in range(args.days):
        day = today + timedelta(days=offset)
        items = [t for t in db["topics"] if is_active(t, day) and date.fromisoformat(t["next_review"]) == day]
        label = day.strftime("%a %d %b")
        print(f"{label}: " + (", ".join(t["name"] for t in items) if items else "-"))

def cmd_list(args, db, db_path):
    today = date.today()
    for t in sorted(db["topics"], key=lambda x: x["next_review"]):
        status = "" if is_active(t, today) else "  [exam passed]"
        print(f"{fmt_topic(t, today)} | next {t['next_review']} | reps {t['reps']} | ease {t['ease']:.2f}{status}")

def cmd_delete(args, db, db_path):
    db["topics"] = [t for t in db["topics"] if t["id"] != args.id]
    save(db, db_path)
    print(f"Deleted #{args.id}.")

def build_parser():
    p = argparse.ArgumentParser(description="Spaced-repetition study planner")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    a = sub.add_parser("add")
    a.add_argument("name")
    a.add_argument("--subject", "-s")
    a.add_argument("--exam", "-e")
    a.set_defaults(fn=cmd_add)
    
    sub.add_parser("today").set_defaults(fn=cmd_today)
    sub.add_parser("review").set_defaults(fn=cmd_review)
    
    pl = sub.add_parser("plan")
    pl.add_argument("--days", "-d", type=int, default=7)
    pl.set_defaults(fn=cmd_plan)
    
    sub.add_parser("list").set_defaults(fn=cmd_list)
    
    d = sub.add_parser("delete")
    d.add_argument("id", type=int)
    d.set_defaults(fn=cmd_delete)
    
    return p
