# Validation

**Setup:** DockQ running with `flask --app app run --debug` on port 5000, PostgreSQL 17 in Docker, tested on Windows. Date tested: 11/11/2026

## 1. Browser layer

The form attributes match the column sizes and NOT NULL rules.

| Field | Column | Attributes in the form |
| :---- | :---- | :---- |
| Driver name | `tickets.driver_name` varchar(80) NOT NULL | `required`, `maxlength="80"` |
| Plate number | `trucks.plate` varchar(12) NOT NULL UNIQUE | `required`, `maxlength="12"`, capital letters only (JavaScript) |
| Type of vehicle | `trucks.vehicle_type` varchar(20) NOT NULL | `required` on the select |
| Company | `companies.name` varchar(120), optional | `maxlength="120"`, not required |
| What do you need? | `tickets.service_id` NOT NULL | `required` on the select |
| Service name (Manage services) | `services.name` varchar(60) NOT NULL UNIQUE | `required`, `maxlength="60"` |
| Average minutes (Manage services) | `services.avg_minutes` integer, CHECK > 0 | `required`, `type="number"`, `min="1"` |

## 2. Flask layer (skipping the form with curl)

| Rule | Layer | How I tested it | What happened |
| :---- | :---- | :---- | :---- |
| Name, plate and service must be valid | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "driver=" -d "plate=ab" -d "service_id=999"` | HTTP/1.1 400 BAD REQUEST |
| Plate must be capital letters, numbers, spaces and dashes | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "driver=Mika" -d "plate=bad id!!" -d "service_id=1"` | HTTP/1.1 400 BAD REQUEST |
| Name must be 80 characters or fewer | Flask | `curl.exe` with a 200-character name | HTTP/1.1 400 BAD REQUEST |
| All fields are required | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join` with no data | HTTP/1.1 400 BAD REQUEST |
| A switched-off service cannot be joined | Flask | `curl.exe` with the `service_id` of a service that is switched off | HTTP/1.1 400 BAD REQUEST |
| Data only changes with POST | Flask | `curl.exe -i http://127.0.0.1:5000/staff/call-next` | HTTP/1.1 400 BAD REQUEST |
| Only known staff actions are accepted | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/staff/1/bogus` | HTTP/1.1 400 BAD REQUEST |
| A missing ticket is a 404, not a crash | Flask | `curl.exe -i http://127.0.0.1:5000/queue/99999` | HTTP/1.1 400 BAD REQUEST |

## 3. Database layer (skipping Flask with psql)

Run with `docker compose exec db psql -U dockq -d dockq`. Each of these must fail with an `ERROR`.

| Rule | Layer | How I tested it | What happened |
| :---- | :---- | :---- | :---- |
| Status must be one of four values | CHECK | `UPDATE tickets SET status = 'lost' WHERE id = 1;` | `ERROR:  new row for relation "tickets" violates check constraint "ck_tickets_status"` |
| A plate must be 4 to 12 capital letters, numbers, spaces or dashes | CHECK | `INSERT INTO trucks (plate, vehicle_type) VALUES ('ab','other');` | `ERROR:  new row for relation "trucks" violates check constraint "ck_trucks_plate"` |
| Average minutes must be above 0 | CHECK | `INSERT INTO services (name, avg_minutes) VALUES ('Test', 0);` | `ERROR:  new row for relation "services" violates check constraint "ck_services_avg_minutes"` |
| One company per name | UNIQUE | `INSERT INTO companies (name) SELECT name FROM companies LIMIT 1;` | `ERROR:  duplicate key value violates unique constraint "companies_name_key"` and `DETAIL:  Key (name)=(Antigonous Corp.) already exists.` |
| A ticket needs a driver name | NOT NULL | `INSERT INTO tickets (truck_id, service_id) VALUES (1, 1);` | `ERROR:  null value in column "driver_name" of relation "tickets" violates not-null constraint` |
| A service with tickets cannot be deleted | ON DELETE RESTRICT | `DELETE FROM services WHERE id = 1;` | `ERROR:  update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets"` and `DETAIL:  Key (id)=(1) is still referenced from table "tickets".` |


A good insert fills in the defaults:

```sql
INSERT INTO tickets (driver_name, truck_id, service_id) VALUES ('Test Driver', 1, 1) RETURNING id, status, created_at;
```

Result:



## 4. No SQL in f-strings

Gluing user input into a SQL string lets the input become code (SQL injection). SQLAlchemy sends values separately from the SQL, so this does not happen. I checked that my code never builds SQL by hand using the command:

```
git grep -nE 'f["''].*(SELECT|INSERT|UPDATE|DELETE)' -- '*.py'
```



## Which error was most useful

I find the error below to be the most useful because it stops a plate that is too short or has bad characters from reaching the table, even when someone skips the form.

```
ERROR:  new row for relation "trucks" violates check constraint "ck_trucks_plate"
```
