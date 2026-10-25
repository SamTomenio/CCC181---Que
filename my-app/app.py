from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable

SERVICES = [
    {"id": 1, "name": "Loading"},
    {"id": 2, "name": "Unloading"},
]

# status: waiting, called, served, no-show
TICKETS = [
    {"number": 1, "driver": "Ramon", "plate": "ABC 1234", "company": "North Freight",
     "service_id": 1, "status": "waiting", "bay": None},
    {"number": 2, "driver": "Joel", "plate": "XYZ 5678", "company": "Metro Haulers",
     "service_id": 2, "status": "waiting", "bay": None},
]

STATUS_LABELS = {"waiting": "Waiting", "called": "Called", "served": "Served", "no-show": "No-show"}
STATUS_COLORS = {"waiting": "warning", "called": "success", "served": "secondary", "no-show": "danger"}


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
        message = f"Please proceed to bay {t['bay']}." if t["bay"] else "You are called. Please proceed to the dock."
    elif t["status"] == "served":
        message = "Done. Thank you!"
    else:
        message = "This ticket is no longer in the queue."
    return {"status": t["status"], "label": STATUS_LABELS[t["status"]],
            "color": STATUS_COLORS[t["status"]], "message": message}


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
    if len(plate) < 4:
        errors["plate"] = "Enter the truck's plate number."
    elif any(t["plate"] == plate and t["status"] in ("waiting", "called") for t in TICKETS):
        errors["plate"] = "This truck is already in the queue."
    if not company:
        errors["company"] = "Enter the company name."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose Loading or Unloading."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({"number": number, "driver": driver, "plate": plate, "company": company,
                    "service_id": service_id, "status": "waiting", "bay": None})
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    return render_template("ticket.html", ticket=t, service=service, info=describe(t))


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)
    t["status"] = "no-show"
    flash("You left the queue.", "info")
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
    if service_id:
        queue = [t for t in queue if t["service_id"] == service_id]
    names = {s["id"]: s["name"] for s in SERVICES}
    counts = {s["id"]: sum(1 for t in TICKETS
                           if t["service_id"] == s["id"] and t["status"] == "waiting")
              for s in SERVICES}
    return render_template("staff.html", queue=queue, services=SERVICES,
                           names=names, counts=counts, selected=service_id)


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    bay = request.form.get("bay", "").strip()
    waiting = [t for t in TICKETS if t["status"] == "waiting"
               and (not service_id or t["service_id"] == service_id)]
    if not waiting:
        flash("No trucks are waiting.", "warning")
    else:
        t = waiting[0]
        t["status"] = "called"
        t["bay"] = bay or None
        flash(f"Truck {t['plate']} (ticket #{t['number']}) called.", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = {"call": "called", "serve": "served", "no-show": "no-show"}.get(action)
    t = find_ticket(ticket_id)
    if t is None or new_status is None:
        abort(404)
    t["status"] = new_status
    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    return redirect(url_for("staff_dashboard")
                    
                    )