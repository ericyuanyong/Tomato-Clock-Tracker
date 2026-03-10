import os
import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from pathlib import Path


# -----------------------------
# CONFIG (edit these)
# -----------------------------

# Where your sqlite db is
DB_PATH = os.environ.get("TOMATO_DB", str(Path.home() / "tomato.db"))

# 163 SMTP settings (SSL)
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465  # SSL

EMAIL_FROM = os.environ.get("MAIL_FROM")
EMAIL_AUTH_CODE = os.environ.get("MAIL_PASS")

# Recipient (your work/personal email)
EMAIL_TO = os.environ.get("MAIL_TO")




# -----------------------------
# Reporting helpers
# -----------------------------
def _make_bar(count: int, max_count: int, width: int = 20) -> str:
    """ASCII bar scaled to max_count."""
    if max_count <= 0 or count <= 0:
        return ""
    n = int(round((count / max_count) * width))
    if n == 0:
        n = 1
    return "█" * n


def get_week_stats_mon_sun():
    """
    Build report for the current week: Monday 00:00 -> next Monday 00:00 (LOCAL time),
    but query DB using UTC ISO strings (Particle published_at is typically UTC ISO8601).

    Returns:
      week_start_local (datetime)
      week_end_local (datetime)  # next Monday
      total_sessions (int)
      week_days (list[str])      # YYYY-MM-DD local dates Mon..Sun
      counts (dict[str,int])     # day -> sessions
    """
    now_local = datetime.now().astimezone()
    monday_local = (now_local - timedelta(days=now_local.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    next_monday_local = monday_local + timedelta(days=7)

    # Convert local week range to UTC for DB compare
    start_utc = monday_local.astimezone(timezone.utc)
    end_utc = next_monday_local.astimezone(timezone.utc)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute(
        """
        SELECT substr(published_at, 1, 10) AS day, COUNT(*) AS sessions
        FROM tomato_events
        WHERE published_at >= ? AND published_at < ?
        GROUP BY day
        ORDER BY day
        """,
        (
            start_utc.isoformat().replace("+00:00", "Z"),
            end_utc.isoformat().replace("+00:00", "Z"),
        ),
    )
    rows = cur.fetchall()
    con.close()

    # Mon..Sun local dates
    week_days = [(monday_local + timedelta(days=i)).date().isoformat() for i in range(7)]

    # Fill missing days with 0
    counts = {day: 0 for day in week_days}
    for day, sessions in rows:
        if day in counts:
            counts[day] = sessions

    total = sum(counts.values())
    return monday_local, next_monday_local, total, week_days, counts


def build_report_text():
    week_start_local, week_end_local, total, week_days, counts = get_week_stats_mon_sun()

    focus_minutes = total * 30
    focus_hours = focus_minutes / 60.0

    max_day = max(counts.values()) if counts else 0
    week_end_sun = (week_end_local.date() - timedelta(days=1))  # Sunday date

    lines = []
    lines.append("🍅 Tomato Clock Weekly Report")
    lines.append(f"Week (Local): {week_start_local.date()} (Mon) → {week_end_sun} (Sun)")
    lines.append("")
    lines.append(f"Total sessions: {total}")
    lines.append(f"Focus time: {focus_minutes} minutes ({focus_hours:.1f} hours)")
    lines.append("")
    lines.append("Daily breakdown (Mon → Sun):")

    # Always print Mon..Sun even if 0
    for day in week_days:
        dt = datetime.strptime(day, "%Y-%m-%d")
        wd = dt.strftime("%a")  # Mon/Tue/...
        c = counts[day]
        bar = _make_bar(c, max_day, width=20)
        lines.append(f"  {wd} {day} | {bar:<20} {c}")

    lines.append("")
    lines.append("— Sent automatically from your SBC. No need to reply")

    subject = f"Tomato weekly report 🍅 ({total} sessions)"
    return subject, "\n".join(lines)


# -----------------------------
# Send email via 163 SMTP SSL
# -----------------------------
def send_email(subject: str, body: str):
    if not EMAIL_FROM or not EMAIL_AUTH_CODE or not EMAIL_TO:
        raise RuntimeError("Email config missing: MAIL_FROM / MAIL_PASS / MAIL_TO")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_AUTH_CODE)  # 163 uses authorization code (授权码)
        smtp.send_message(msg)


def main():
    subject, body = build_report_text()
    print(body)  # helpful when testing
    send_email(subject, body)
    print("Email sent successfully via 163 SMTP.")


if __name__ == "__main__":
    main()