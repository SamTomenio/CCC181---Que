# Schema self-review

My starting point was ClinicQ's three tables. These are the problems I found when I reviewed my schema for DockQ.

## Who is a person? Drivers, trucks and companies

**Works well:** `trucks.plate` is NOT NULL, UNIQUE and has a CHECK for capitals, numbers, spaces and hyphens, so a truck is stored once and a badly typed plate cannot reach the table.

**Problem:** ClinicQ's `users` table treats a person's email as their identity. At the bay, the person is a driver with a truck, and a different driver may bring the same truck on another day. If I put the driver's name on `trucks`, a new driver would overwrite the old one, and old tickets would show the wrong name.

**Change:** The truck is the stable thing, so `plate` is the unique identity in `trucks`. The driver's name is a fact about one visit, so it is `tickets.driver_name`. I did not add a `users` table.

## Company copied onto every row

**Works well:** Splitting trucks from tickets means a plate is stored once, however many times the truck joins.

**Problem:** In Week 3 the company was a text field typed on every join. The same company would appear as "North Freight", "north freight" and "North Frieght", which breaks the 3NF rule (a hidden copy of one fact in many rows) and would make a per-company report wrong.

**Change:** A `companies` table holds each name once (NOT NULL UNIQUE), and `trucks.company_id` points to it. The join route strips the spaces and looks up an existing company before creating a new one.

## The same truck in the queue twice

**Works well:** `trucks.plate` is UNIQUE, so two trucks can never share a plate.

**Problem:** A UNIQUE plate does not stop one truck from having two tickets. A double tap, or the driver joining again from a second phone, would create two open tickets and put the truck in line twice. That breaks NFR-03, and the Python check is not enough if two requests arrive at the same moment.

**Change:** A unique partial index on `tickets(truck_id)` where `status IN ('waiting', 'called')` lets a truck have only one open ticket. The join route catches the `IntegrityError`, rolls back, and tells the driver the truck is already in the queue. A finished ticket does not block joining again later.

## Vehicle type: free text or fixed list

**Works well:** The vehicle type is a fact about the truck, so it belongs in `trucks`, not on every ticket.

**Problem:** My first idea was a plain text box. The dispatcher asked for types like 4-wheeler and 8-wheeler (FR-14), but free text would give "8 wheeler", "8-wheeler" and "eight wheeler", and the dashboard could not filter or count them.

**Change:** `trucks.vehicle_type` is NOT NULL with a CHECK that allows only `4-wheeler`, `6-wheeler`, `8-wheeler`, `10-wheeler` and `other`, and the join form uses a dropdown with the same values.
