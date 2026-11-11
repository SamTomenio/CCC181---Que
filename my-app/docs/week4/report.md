# DockQ: Week 4 Report

## Title details

- **App:** DockQ
- **Setting:** Truck loading and unloading bay, Iligan City
- **Name:** Tomenio, Sam B.
- **Student ID:** 20241845
- **Section:** CS3A
- **Date:** 11/11/2026
- **Database:** PostgreSQL 17 in Docker
- **Pull request:** 

## Requirements

I wrote 14 functional requirements and 8 non-functional requirements in [docs/requirements.md](../requirements.md).

**MVP:** TODO-4 (copy the MVP list and the one or two sentences of reasoning from `docs/requirements.md`).

**Checked with a real person:** I showed the list to a dispatcher and a truck driver. The dispatcher said the app should record what kind of vehicle each truck is (4-wheeler, 8-wheeler and so on). I changed: added a vehicle type to every truck and a dropdown on the join form (TODO-5: requirement ID). The driver said all trucks carry goods, so I did not add a cargo type.

## ERD

![ERD](erd.png)

- One company has many trucks. Each truck belongs to one company, or to none when the company is not given.
- One truck has many tickets. Each ticket belongs to exactly one truck.
- One service has many tickets. Each ticket belongs to exactly one service.
- A truck can have only one open ticket (waiting or called) at a time, enforced by a partial unique index.

Full design, with every column, type and constraint: [schema.md](schema.md)

## Schema

TODO-6: paste the real output of each command below inside a code block, one block per table.

```
                                    Table "public.companies"
 Column |          Type          | Collation | Nullable |                Default                
--------+------------------------+-----------+----------+---------------------------------------
 id     | integer                |           | not null | nextval('companies_id_seq'::regclass)
 name   | character varying(120) |           | not null | 



                                      Table "public.trucks"
    Column    |         Type          | Collation | Nullable |              Default               
--------------+-----------------------+-----------+----------+------------------------------------
 id           | integer               |           | not null | nextval('trucks_id_seq'::regclass)
 plate        | character varying(12) |           | not null | 
 vehicle_type | character varying(20) |           | not null | 
 company_id   | integer               |           |          | 

                                      Table "public.services"
   Column    |         Type          | Collation | Nullable |               Default                
-------------+-----------------------+-----------+----------+--------------------------------------
 id          | integer               |           | not null | nextval('services_id_seq'::regclass)
 name        | character varying(60) |           | not null | 
 avg_minutes | integer               |           | not null | 
 active      | boolean               |           | not null | true



                                       Table "public.tickets"
     Column     |           Type           | Collation | Nullable |               Default               
----------------+--------------------------+-----------+----------+-------------------------------------
 id             | integer                  |           | not null | nextval('tickets_id_seq'::regclass)
 driver_name    | character varying(80)    |           | not null | 
 status         | character varying(10)    |           | not null | 
 bay            | character varying(20)    |           |          | 
 arrive_by      | time without time zone   |           |          | 
 created_at     | timestamp with time zone |           | not null | now()
 called_at      | timestamp with time zone |           |          | 
 closed_at      | timestamp with time zone |           |          | 
 driver_ok_at   | timestamp with time zone |           |          | 
 driver_deleted | boolean                  |           | not null | 
 truck_id       | integer                  |           | not null | 
 service_id     | integer                  |           | not null | 

```

## Design decisions

1. **A truck has one plate, and a plate can have only one open ticket.** TODO-7: write which requirement this meets (the "no one else can take their place" rule) and why a partial unique index was better than checking only in Python.
2. **Vehicle type lives on `trucks`, not on `tickets`.** The dispatcher told me a truck's type does not change from visit to visit, so it is a fact about the truck. It is limited to 4-wheeler, 6-wheeler, 8-wheeler, 10-wheeler, trailer and other by a CHECK constraint.
3. **Position in line is computed, not stored.** For the My place page I count the waiting tickets for the same service that joined earlier, so there is no position column to rewrite whenever a truck joins or leaves.

## Self-review

The problems I found in my schema, from [schema-review.md](schema-review.md):

TODO-8: copy the Problem and Change lines from `docs/week4/schema-review.md` as three or more bullets.

## Migrations

- `<hash>_create_companies_trucks_services_tickets.py`: creates the `companies`, `trucks`, `services` and `tickets` tables with their keys, constraints and defaults. TODO-9: replace `<hash>` and the name with the real file name from `dir migrations\versions`.
- `7e9586fb5792_add_services_active.py`: adds the `active` column to `services`, so staff can switch a service off without deleting it.
- `<hash>_add_server_defaults.py`: gives `status`, `vehicle_type` and `driver_deleted` database-level defaults, so rows inserted directly in psql are valid too. TODO-9: use the real file name.

## CRUD

| Operation | Route | Requirement | Screenshot |
|---|---|---|---|
| Create | `POST /join` | TODO-10 | ![Join](screenshots/join.JPG) |
| Read | `GET /queue/<id>` and `GET /staff` | TODO-10 | ![Join success](screenshots/join-success.JPG) ![Staff](screenshots/staff.JPG) |
| Update | `POST /staff/call-next`, `POST /staff/call-selected` and `POST /staff/<id>/<action>` | TODO-10 | ![Staff call](screenshots/staff-call.JPG) ![Staff served](screenshots/staff-served.JPG) |
| Soft delete | `POST /queue/<id>/leave` | TODO-10 | ![Ticket left](screenshots/ticket-left.JPG) |
| Hard delete | `POST /staff/<id>/delete` | TODO-10 | ![Archive delete](screenshots/staff-archive-delete.JPG) ![Staff delete](screenshots/staff-delete.JPG) |
| Manage services | `GET/POST /staff/services` | TODO-10 | TODO-11: add a screenshot of the Manage services page |

## Validation

Full results: [validation.md](validation.md). The browser, Flask and the database all check the data. Requests that skip the form get a 400 and save nothing, and every bad insert in psql fails with a clear error for each constraint type.

The PostgreSQL error I found most useful:

```
ERROR:  new row for relation "trucks" violates check constraint "ck_trucks_plate"
```

TODO-12: say in your own words why this error was the most useful to you.

## Persistence

![Dashboard before restart](screenshots/Before-Restart-Staff-Part1.JPG)
![Table before restart](screenshots/table-before-restart.JPG)

![Dashboard after restart](screenshots/staff.JPG)
![Table after restart](screenshots/table-after-restart.JPG)

No ticket was lost on restart, so TODO-13 (requirement ID) is satisfied. TODO-14: add one sentence about the rebuild from scratch. Details: [persistence.md](persistence.md)

## Reflection



## Declaration

I used Claude to help draft my requirements, schema, ERD, models, Docker Compose file, routes, templates and first versions of my documents, adapted from the activity and my Week 3 app. I ran the commands, tested the app, took the screenshots and checked the results myself.
