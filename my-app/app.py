import os
import re
from datetime import datetime, time, timezone

from dotenv import load_dotenv
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_migrate import Migrate
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from models import Company, Service, Ticket, Truck, db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dockq-dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

PLATE_RE = re.compile(r"^[A-Z0-9 -]{4,12}$")
VEHICLE_TYPES = ["4-wheeler", "6-wheeler", "8-wheeler",
                 "10-wheeler", "trailer", "other"]


# ---------- helpers ----------
def now():
    return datetime.now(timezone.utc)


def format_time(dt):
    if not dt:
        return ""
    return dt.astimezone().strftime("%b %d, %Y %I:%M %p")


STATUS_INFO = {
    "waiting": {"label": "Waiting", "color": "warning",
                "message": "You are in the queue. Keep this page open."},
    "called": {"label": "Called", "color": "success",
               "message": "Please proceed to your bay now."},
    "served": {"label": "Served", "color": "secondary",
               "message": "You have been served. Thank you."},
    "left": {"label": "Left", "color": "danger",
             "message": "This ticket is closed."},
}


def describe(t):
    """Turn a Ticket row into a dict the templates can use."""
    position = None
    wait_minutes = None
    if t.status == "waiting":
        ahead = db.session.scalar(
            select(func.count()).select_from(Ticket).where(
                Ticket.status == "waiting", Ticket.created_at < t.created_at))
        position = ahead + 1
        wait_minutes = position * t.service.avg_minutes
    return {
        "id": t.id,
        "number": t.id,
        "name": t.driver_name,
        "driver_name": t.driver_name,
        "driver": t.driver_name,
        "plate": t.truck.plate,
        "company": t.truck.company.name if t.truck.company else "",
        "vehicle_type": t.truck.vehicle_type,
        "service": t.service.name,
        "service_id": t.service_id,
        "status": t.status,
        "info": STATUS_INFO.get(t.status, STATUS_INFO["waiting"]),
        "bay": t.bay,
        "arrive_by": t.arrive_by.strftime("%I:%M %p").lstrip("0") if t.arrive_by else "",
        "arrive_by_value": t.arrive_by.strftime("%H:%M") if t.arrive_by else "",
        "created_at": format_time(t.created_at),
        "joined_at": format_time(t.created_at),
        "called_at": format_time(t.called_at),
        "closed_at": format_time(t.closed_at),
        "driver_ok_at": format_time(t.driver_ok_at),
        "driver_deleted": t.driver_deleted,
        "position": position,
        "wait_minutes": wait_minutes,
    }


def get_ticket_or_404(ticket_id):
    t = db.session.get(Ticket, ticket_id)
    if t is None:
        abort(404)
    return t


def parse_time(value):
    try:
        h, m = (value or "").split(":")[:2]
        return time(int(h), int(m))
    except (ValueError, TypeError):
        return None


def my_ids():
    return session.get("my_tickets", [])


def waiting_counts():
    rows = db.session.execute(
        select(Ticket.service_id, func.count()).where(Ticket.status == "waiting")
        .group_by(Ticket.service_id)).all()
    counts = {sv.id: 0 for sv in all_services()}
    counts.update({sid: n for sid, n in rows})
    return counts


def all_services():
    return db.session.scalars(select(Service).order_by(Service.name)).all()


def active_services():
    return db.session.scalars(
        select(Service).where(Service.active.is_(True)).order_by(Service.name)).all()


@app.context_processor
def inject_my_archive():
    ids = my_ids()
    archive = []
    if ids:
        rows = db.session.scalars(
            select(Ticket).where(Ticket.id.in_(ids),
                                 Ticket.status.in_(["served", "left"]),
                                 Ticket.driver_deleted.is_(False))
            .order_by(Ticket.closed_at.desc())).all()
        archive = [describe(t) for t in rows]
    return {"my_archive": archive, "services": active_services(),
        "names": {sv.id: sv.name for sv in all_services()},
        "service_names": {sv.id: sv.name for sv in all_services()},
        "counts": waiting_counts(),
        "vehicle_types": VEHICLE_TYPES}


# ---------- driver side ----------
@app.route("/")
def index():
    waiting = db.session.scalar(
        select(func.count()).select_from(Ticket).where(Ticket.status == "waiting"))
    return render_template("index.html", waiting_count=waiting)


class Errors(dict):
    """Works whether the template reads errors.plate or loops over errors."""

    def __iter__(self):
        return iter(self.values())


def show_join(errors=None, form=None, status=200):
    return render_template("join.html", errors=Errors(errors or {}),
                           form=form or {}, values=form or {}), status


@app.route("/join")
def join_form():
    return show_join()


@app.route("/join", methods=["POST"])
def join():
    driver_name = (request.form.get("driver") or request.form.get("driver_name")
                   or request.form.get("name") or "").strip()
    plate = (request.form.get("plate") or "").strip().upper()
    company_name = (request.form.get("company") or "").strip()
    vehicle_type = request.form.get("vehicle_type") or "other"
    service_value = request.form.get("service") or request.form.get("service_id") or ""

    errors = {}
    if not driver_name:
        errors["name"] = "Please enter the driver's name."
        errors["driver_name"] = errors["name"]
        errors["driver"] = errors["name"]
    if not PLATE_RE.match(plate):
        errors["plate"] = "Plate must be 4-12 characters: capital letters, numbers, space or dash."
    if vehicle_type not in VEHICLE_TYPES:
        vehicle_type = "other"

    service = None
    if service_value.isdigit():
        service = db.session.get(Service, int(service_value))
    if service is None and service_value:
        service = db.session.scalar(
            select(Service).where(func.lower(Service.name) == service_value.lower()))
    if service is None or not service.active:
        service = None
        errors["service"] = "Please choose Loading or Unloading."
        errors["service_id"] = errors["service"]

    if errors:
        return show_join(errors, request.form, 400)

    company = None
    if company_name:
        company = db.session.scalar(select(Company).where(Company.name == company_name))
        if company is None:
            company = Company(name=company_name)
            db.session.add(company)
            db.session.flush()

    truck = db.session.scalar(select(Truck).where(Truck.plate == plate))
    if truck is None:
        truck = Truck(plate=plate, vehicle_type=vehicle_type,
                      company_id=company.id if company else None)
        db.session.add(truck)
        db.session.flush()

    ticket = Ticket(driver_name=driver_name, truck_id=truck.id,
                    service_id=service.id)
    db.session.add(ticket)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return show_join({"plate": f"Truck {plate} is already in the queue."},
                         request.form, 400)

    session["my_tickets"] = my_ids() + [ticket.id]
    return redirect(url_for("ticket", ticket_id=ticket.id))


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = get_ticket_or_404(ticket_id)
    d = describe(t)
    ahead = (d["position"] - 1) if d["position"] else 0
    return render_template("ticket.html", ticket=d, t=d, service=t.service,
                           ahead=ahead, info=d["info"])


@app.route("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    return jsonify(describe(get_ticket_or_404(ticket_id)))


@app.route("/queue/<int:ticket_id>/leave", methods=["POST"])
def leave(ticket_id):
    t = get_ticket_or_404(ticket_id)
    if t.status in ("waiting", "called"):
        t.status = "left"
        t.closed_at = now()
        db.session.commit()
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.route("/queue/<int:ticket_id>/ok", methods=["POST"])
def driver_ok(ticket_id):
    t = get_ticket_or_404(ticket_id)
    if t.status in ("served", "left") and not t.driver_ok_at:
        t.driver_ok_at = now()
        db.session.commit()
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.route("/queue/<int:ticket_id>/delete", methods=["POST"])
def driver_delete(ticket_id):
    t = get_ticket_or_404(ticket_id)
    if t.status in ("served", "left"):
        t.driver_deleted = True
        db.session.commit()
    return redirect(url_for("index"))


# ---------- staff side ----------
@app.route("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    stmt = (select(Ticket).where(Ticket.status.in_(["waiting", "called"]))
            .order_by(Ticket.created_at))
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    active = db.session.scalars(stmt).all()
    archive = db.session.scalars(
        select(Ticket).where(Ticket.status.in_(["served", "left"]))
        .order_by(Ticket.closed_at.desc())).all()
    active_d = [describe(t) for t in active]
    return render_template(
        "staff.html",
        queue=active_d,
        tickets=active_d,
        waiting=[d for d in active_d if d["status"] == "waiting"],
        called=[d for d in active_d if d["status"] == "called"],
        archive=[describe(t) for t in archive],
        services=all_services(),
        selected=service_id,
    )


def mark_called(t, bay, arrive_by):
    t.status = "called"
    t.called_at = now()
    t.bay = bay or None
    t.arrive_by = arrive_by


@app.route("/staff/call-next", methods=["POST"])
def call_next():
    stmt = select(Ticket).where(Ticket.status == "waiting")
    sid = request.form.get("service_id", type=int)
    if sid:
        stmt = stmt.where(Ticket.service_id == sid)
    t = db.session.scalar(stmt.order_by(Ticket.created_at).limit(1))
    if t is None:
        flash("Nobody is waiting.", "info")
    else:
        mark_called(t, request.form.get("bay", "").strip(),
                    parse_time(request.form.get("arrive_by")))
        db.session.commit()
    return redirect(url_for("staff_dashboard"))


@app.route("/staff/call-selected", methods=["POST"])
def call_selected():
    ids = [int(i) for i in (request.form.getlist("ticket_ids") or request.form.getlist("selected")) if i.isdigit()]
    if not ids:
        flash("Select at least one truck.", "warning")
        return redirect(url_for("staff_dashboard"))
    bay = request.form.get("bay", "").strip()
    arrive_by = parse_time(request.form.get("arrive_by"))
    for t in db.session.scalars(
            select(Ticket).where(Ticket.id.in_(ids), Ticket.status == "waiting")):
        mark_called(t, bay, arrive_by)
    db.session.commit()
    return redirect(url_for("staff_dashboard"))


@app.route("/staff/<int:ticket_id>/<action>", methods=["POST"])
def staff_action(ticket_id, action):
    t = get_ticket_or_404(ticket_id)
    if action == "serve" and t.status in ("waiting", "called"):
        t.status = "served"
        t.closed_at = now()
    elif action in ("noshow", "no-show", "no_show") and t.status in ("waiting", "called"):
        t.status = "left"
        t.closed_at = now()
    elif action == "call" and t.status == "waiting":
        mark_called(t, request.form.get("bay", "").strip(),
                    parse_time(request.form.get("arrive_by")))
    else:
        abort(400)
    db.session.commit()
    return redirect(url_for("staff_dashboard"))


@app.route("/staff/<int:ticket_id>/delete", methods=["POST"])
def staff_delete(ticket_id):
    t = get_ticket_or_404(ticket_id)
    db.session.delete(t)  # hard delete: the row is gone for good
    db.session.commit()
    flash(f"Ticket {t.id} was deleted.", "warning")
    return redirect(url_for("staff_dashboard"))


# ---------- manage services ----------
@app.route("/staff/services")
def services_list():
    rows = db.session.scalars(select(Service).order_by(Service.name)).all()
    counts = {s.id: len(s.tickets) for s in rows}
    return render_template("services.html", all_services=rows, counts=counts,
                           services=rows)


@app.route("/staff/services", methods=["POST"])
def service_create():
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    if not name or len(name) > 60 or not minutes or minutes <= 0:
        flash("Enter a name (up to 60 characters) and minutes greater than 0.", "danger")
        return redirect(url_for("services_list"))
    db.session.add(Service(name=name, avg_minutes=minutes))
    try:
        db.session.commit()
        flash(f"Service \u201c{name}\u201d added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named \u201c{name}\u201d already exists.", "danger")
    return redirect(url_for("services_list"))


@app.route("/staff/services/<int:service_id>/edit", methods=["POST"])
def service_edit(service_id):
    s = db.session.get(Service, service_id)
    if s is None:
        abort(404)
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    if not name or len(name) > 60 or not minutes or minutes <= 0:
        flash("Enter a name (up to 60 characters) and minutes greater than 0.", "danger")
        return redirect(url_for("services_list"))
    s.name = name
    s.avg_minutes = minutes
    s.active = request.form.get("active") == "on"
    try:
        db.session.commit()
        flash(f"Service \u201c{name}\u201d updated.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named \u201c{name}\u201d already exists.", "danger")
    return redirect(url_for("services_list"))


@app.route("/staff/services/<int:service_id>/delete", methods=["POST"])
def service_delete(service_id):
    s = db.session.get(Service, service_id)
    if s is None:
        abort(404)
    if s.tickets:
        flash(f"\u201c{s.name}\u201d has tickets, so it cannot be deleted. Turn it off instead.", "danger")
        return redirect(url_for("services_list"))
    name = s.name
    db.session.delete(s)
    db.session.commit()
    flash(f"Service \u201c{name}\u201d deleted.", "warning")
    return redirect(url_for("services_list"))


# ---------- seed data ----------
@app.cli.command("seed")
def seed():
    """Add the two services if they don't exist."""
    for name, minutes in [("Loading", 30), ("Unloading", 25)]:
        if not db.session.scalar(select(Service).where(Service.name == name)):
            db.session.add(Service(name=name, avg_minutes=minutes))
    db.session.commit()
    print("Seeded services.")