import re
from datetime import datetime
from itertools import count

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable

SERVICES = [
    {"id": 1, "name": "Loading"},
    {"id": 2, "name": "Unloading"},
]

# status: waiting, called, served, no-show
TICKETS = [
    {"number": 1, "driver": "Ramon", "plate": "ABC 1234", "company": "North Freight",
     "service_id": 1, "status": "waiting", "bay": None, "arrive_by": None,
     "joined_at": None, "closed_at": None, "driver_ok_at": None, "driver_deleted": False},
    {"number": 2, "driver": "Joel", "plate": "XYZ 5678", "company": "Metro Haulers",
     "service_id": 2, "status": "waiting", "bay": None, "arrive_by": None,
     "joined_at": None, "closed_at": None, "driver_ok_at": None, "driver_deleted": False},
]

# Ticket numbers only go up and are never reused, even after a delete
ticket_numbers = count(3)

STATUS_LABELS = {"waiting": "Waiting", "called": "Called", "served": "Served", "no-show": "No-show"}
STATUS_COLORS = {"waiting": "warning", "called": "success", "served": "secondary", "no-show": "danger"}


def now_text():
    return datetime.now().strftime("%b %d, %Y %I:%M %p")


def format_time(value):
    """Turn '14:30' from a time input into '2:30 PM'. Returns None if empty or invalid."""
    try:
        return datetime.strptime(value, "%H:%M").strftime("%I:%M %p").lstrip("0")
    except (TypeError, ValueError):
        return None


def find_ticket(ticket_id):
    return next((t for t in TICKETS if t["number"] == ticket_id), None)


def count_ahead(t):
    return sum(1 for x in TICKETS
               if x["service_id"] == t["service_id"]
               and x["status"] == "waiting" and x["number"] < t["number"])


def describe(t):
    """Text for My place. Used by the page and by the JSON route, so they always match."""
    ahead = count_ahead(t)
    if t["status"] == "waiting":
        message = "You're next!" if ahead == 0 else f"{ahead} truck{'s' if ahead != 1 else ''} ahead of you"
    elif t["status"] == "called":
        message = (f"Please proceed to bay {t['bay']}." if t.get("bay")
                   else "You are called. Please proceed to the dock.")
        if t.get("arrive_by"):
            message += f" Arrive by {t['arrive_by']}."
    elif t["status"] == "served":
        message = "Done. Thank you!"
    else:
        message = "This ticket is no longer in the queue."
    return {"status": t["status"], "label": STATUS_LABELS[t["status"]],
            "color": STATUS_COLORS[t["status"]], "message": message,
            "bay": t.get("bay"), "arrive_by": t.get("arrive_by")}
@app.context_processor
def inject_my_archive():
    """Makes the driver's archived tickets available to every page (for the slide-in panel)."""
    mine = []
    for tid in session.get("my_tickets", []):
        t = find_ticket(tid)
        if t and t.get("driver_ok_at") and not t.get("driver_deleted"):
            mine.append(t)
    mine.sort(key=lambda t: t["number"], reverse=True)
    return {"my_archive": mine, "service_names": {s["id"]: s["name"] for s in SERVICES}}


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    return render_template("join.html", services=SERVICES, form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    driver = form.get("driver", "").strip()
    plate = form.get("plate", "").strip().upper()
    company = form.get("company", "").strip()
    service_id = form.get("service_id", type=int)

    errors = {}
    if not driver:
        errors["driver"] = "Enter the driver's name."
    if not re.fullmatch(r"[A-Z0-9 -]{4,12}", plate):
        errors["plate"] = "Use capital letters, numbers, spaces or hyphens only (4 to 12 characters)."
    elif any(t["plate"] == plate and t["status"] in ("waiting", "called") for t in TICKETS):
        errors["plate"] = "This truck is already in the queue."
    if not company:
        errors["company"] = "Enter the company name."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose Loading or Unloading."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    number = next(ticket_numbers)
    TICKETS.append({"number": number, "driver": driver, "plate": plate, "company": company,
                    "service_id": service_id, "status": "waiting", "bay": None, "arrive_by": None,
                    "joined_at": now_text(), "closed_at": None,
                    "driver_ok_at": None, "driver_deleted": False})

    # Remember this ticket in the driver's browser so it can appear in "My tickets"
    session.permanent = True
    mine = session.get("my_tickets", [])
    mine.append(number)
    session["my_tickets"] = mine

    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = find_ticket(ticket_id)
    if t is None or t.get("driver_deleted"):
        abort(404)
    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    return render_template("ticket.html", ticket=t, service=service, info=describe(t))


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    t["status"] = "no-show"
    t["closed_at"] = now_text()
    flash("You left the queue.", "info")
    return redirect(url_for("index"))


@app.post("/queue/<int:ticket_id>/ok")
def driver_ok(ticket_id):
    """Driver confirms the ticket is finished. This archives it for them."""
    t = find_ticket(ticket_id)
    if t is None or t.get("driver_deleted"):
        abort(404)
    if t["status"] in ("served", "no-show") and not t.get("driver_ok_at"):
        t["driver_ok_at"] = now_text()
        flash("Thanks! Your ticket was archived. Find it under My tickets.", "success")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.post("/queue/<int:ticket_id>/delete")
def driver_delete(ticket_id):
    """Driver removes the finished ticket from their side. Staff keep their archive record."""
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    if t["status"] not in ("served", "no-show"):
        flash("You can only delete a ticket after it is finished.", "warning")
        return redirect(url_for("ticket", ticket_id=ticket_id))
    t["driver_deleted"] = True
    flash("Ticket deleted from your history.", "info")
    return redirect(url_for("index"))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    return describe(t)


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    queue = [t for t in TICKETS if t["status"] in ("waiting", "called")]
    archive = [t for t in TICKETS if t["status"] in ("served", "no-show")]
    if service_id:
        queue = [t for t in queue if t["service_id"] == service_id]
        archive = [t for t in archive if t["service_id"] == service_id]
    archive.sort(key=lambda t: t["number"], reverse=True)  # newest first
    names = {s["id"]: s["name"] for s in SERVICES}
    counts = {s["id"]: sum(1 for t in TICKETS
                           if t["service_id"] == s["id"] and t["status"] == "waiting")
              for s in SERVICES}
    return render_template("staff.html", queue=queue, archive=archive, services=SERVICES,
                           names=names, counts=counts, selected=service_id)


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    bay = request.form.get("bay", "").strip()
    arrive_by = format_time(request.form.get("arrive_by", ""))
    waiting = [t for t in TICKETS if t["status"] == "waiting"
               and (not service_id or t["service_id"] == service_id)]
    if not waiting:
        flash("No trucks are waiting.", "warning")
    else:
        t = waiting[0]
        t["status"] = "called"
        t["bay"] = bay or None
        t["arrive_by"] = arrive_by
        extra = f", arrive by {arrive_by}" if arrive_by else ""
        flash(f"Truck {t['plate']} (ticket #{t['number']}) called{extra}.", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = {"call": "called", "serve": "served", "no-show": "no-show"}.get(action)
    t = find_ticket(ticket_id)
    if t is None or new_status is None:
        abort(404)
    t["status"] = new_status
    if new_status == "called":
        t["bay"] = request.form.get("bay", "").strip() or None
        t["arrive_by"] = format_time(request.form.get("arrive_by", ""))
    if new_status in ("served", "no-show"):
        t["closed_at"] = now_text()
        flash(f"Ticket #{ticket_id} marked {new_status} and moved to the archive.", "info")
    else:
        flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    return redirect(url_for("staff_dashboard"))


@app.post("/staff/tickets/<int:ticket_id>/delete")
def staff_delete(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    if t["status"] not in ("served", "no-show"):
        flash("Only archived tickets can be deleted.", "warning")
    else:
        TICKETS.remove(t)
        flash(f"Ticket #{ticket_id} deleted from the archive.", "info")
    return redirect(url_for("staff_dashboard"))