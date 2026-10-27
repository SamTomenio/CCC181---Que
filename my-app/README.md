# DockQ: Truck Loading and Unloading Queue

DockQ is a queue system for trucks waiting to load or unload at Iligan City. Drivers join from their
phone and see their place in line; dock staff call, serve or mark no-show. Run it and immediately use
the system.

Built for **CCC181 Week 3: Start Your Own Queue App** with Flask, Jinja and Bootstrap 5.

> **Note:** the staff dashboard has no login yet (staff login comes in a later week), so anyone who
> opens `/staff` can use it. Data is kept in memory, so it resets every time the server restarts.
> Week 4 moves it into PostgreSQL.

## Who it is for

| Person | Persona | What they do |
| --- | --- | --- |
| Driver (person waiting) | Ramon | Joins the queue, sees ticket number, trucks ahead, bay and arrive-by time, then archives the ticket |
| Dock staff (dispatcher) | Liza | Sees the waiting list, calls trucks to a bay, marks them served or no-show, and manages the archive |

## Features

**Driver side**
- **Join the queue** for Loading or Unloading (driver name, truck plate in capital letters, company, service)
- **My place** page: large ticket number, status badge, trucks ahead, bay and arrive-by time, and a Leave button
- Page updates itself every 10 seconds, with no reload
- **OK** button after being served, with date and time, then **Delete ticket**
- **My tickets** slide-in panel with archived tickets (from the top menu)

**Staff side**
- Waiting count per service
- Filter by service
- **Call next**, or tick trucks (or select all) and press **Call selected**, with a bay number and an arrive-by time
- Per-row **Call / Update**, **Serve** and **No-show**
- **Archive** table with joined, finished and driver-OK times, and a Delete button

## Project structure

```
app.py                # routes and in-memory data
requirements.txt      # packages to rebuild the environment
.gitignore            # keeps .venv and caches out of Git
templates/
├── base.html         # shared layout, navbar, My tickets panel
├── index.html        # home page
├── join.html         # join form with validation
├── ticket.html       # My place
└── staff.html        # staff dashboard
static/
├── css/style.css
└── js/main.js        # double-submit guard, plate capitals, select-all
docs/week3/           # personas, wireframes, review, accessibility, usability test, report
```

## Routes

| URL | What you see |
| --- | --- |
| `/` | Welcome page with a Join the queue button |
| `/join` | Join form (GET shows it, POST submits it) |
| `/queue/<id>` | My place for one ticket (404 if it does not exist) |
| `/queue/<id>/status.json` | Live status used by My place |
| `/queue/<id>/leave`, `/ok`, `/delete` | Driver actions (POST) |
| `/staff` | Staff dashboard |
| `/staff/call-next`, `/staff/call-selected` | Call trucks (POST) |
| `/staff/tickets/<id>/<call\|serve\|no-show>` | Row actions (POST) |
| `/staff/tickets/<id>/delete` | Delete an archived ticket (POST) |

## Run it

You need Python 3.11 or newer. Run these commands in the folder that contains `app.py`.

**With uv (recommended)**

```bash
uv venv
uv pip install -r requirements.txt
uv run python -m flask --app app run --debug
```

**With plain Python**

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
flask --app app run --debug
```

Then open http://127.0.0.1:5000.

- Stop the server with `Ctrl+C`.
- To try it on a phone on the same Wi-Fi, add `--host 0.0.0.0` and open `http://<your-laptop-ip>:5000`.
- `--debug` reloads the server when you save a file. Never use it in production.

## Try it in 1 minute

1. Open `/join`, enter a driver, a plate such as `DEF 9012`, a company and a service, and press **Get a ticket**.
2. In another tab open `/staff`, tick your truck, enter a bay and an arrive-by time, and press **Call selected**.
3. Back on My place, the status changes to **Called** within 10 seconds, with the bay and time.
4. On Staff press **Serve**, then on My place press **OK** and open **My tickets**.

## Sample data

The app starts with two sample trucks (tickets #1 and #2) so the staff dashboard is not empty.
Edit `SERVICES` and `TICKETS` at the top of `app.py` to change them.

## Git workflow

Work is done on `feature/week3-interface`, merged into `main` with a pull request, and tagged `week3`.

```bash
git switch -c feature/week3-interface
git add .
git commit -m "Describe the change (#issue)"
git push -u origin feature/week3-interface
```

## Roadmap

| Week | Change |
| --- | --- |
| 4 | Tickets move from a Python list into PostgreSQL |
| 6 | The same data is served by a REST API |
| 8 | A Flutter app talks to the API |