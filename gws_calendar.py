import datetime
from gws_auth import get_service

def _parse_deadline(deadline: str) -> tuple:
    """
    Convert a deadline string to a Google Calendar datetime dict.
    Returns (start_dict, end_dict) — event is 1 hour long by default.
    Falls back to tomorrow if deadline is TBD or unparseable.
    """
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    default_start = datetime.datetime.combine(tomorrow, datetime.time(10, 0))

    if not deadline or deadline.strip().upper() in ("TBD", "N/A", ""):
        start_dt = default_start
    else:
        # Try common formats
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                parsed = datetime.datetime.strptime(deadline.strip(), fmt)
                start_dt = parsed.replace(hour=10, minute=0, second=0)
                break
            except ValueError:
                continue
        else:
            start_dt = default_start  # fallback

    end_dt = start_dt + datetime.timedelta(hours=1)

    fmt = "%Y-%m-%dT%H:%M:%S"
    return (
        {"dateTime": start_dt.strftime(fmt), "timeZone": "Asia/Kolkata"},
        {"dateTime": end_dt.strftime(fmt),   "timeZone": "Asia/Kolkata"},
    )

def create_events_from_tasks(tasks: list) -> list:
    """
    Create Google Calendar events for each action item extracted by Hermes.

    Args:
        tasks: List of dicts with keys 'who', 'what', 'deadline'

    Returns:
        List of result dicts with 'task', 'success', and 'event_link' or 'error'
    """
    service = get_service("calendar", "v3")
    results = []

    for task in tasks:
        who      = task.get("who", "Unassigned")
        what     = task.get("what", "No description")
        deadline = task.get("deadline", "TBD")

        start, end = _parse_deadline(deadline)

        event_body = {
            "summary": f"[Hermes] {what}",
            "description": (
                f"Action item from Hermes Smart Meeting Assistant\n\n"
                f"Assigned to: {who}\n"
                f"Task: {what}\n"
                f"Deadline: {deadline}"
            ),
            "start": start,
            "end": end,
        }

        try:
            event = service.events().insert(
                calendarId="primary", body=event_body
            ).execute()
            results.append({
                "task": what,
                "success": True,
                "event_link": event.get("htmlLink"),
            })
        except Exception as e:
            results.append({"task": what, "success": False, "error": str(e)})

    return results
