
# DockQ requirements

**Setting:** Truck loading bay (Pilmico-type), Iligan City. Trucks cannot line up at the bay because the loading area is small, so drivers stay in their cabs or near the gate to find out when their turn comes.
**People who wait:** Truck drivers (loading and unloading). Persona: Ramon, in [docs/week3/personas.md](week3/personas.md).
**People who serve:** Dispatchers at the bay office. Persona: Liza, in [docs/week3/personas.md](week3/personas.md).


**Problem statement:** A truck driver needs a way to know where to go and at what time, without staying at the gate, because the loading area is too small for trucks to line up and long waits with the engine running waste fuel and delay the next trip.


## Functional requirements


IDs FR-01 to FR-08 are from my Week 1 proposal and keep their meaning. FR-09 onward are new.


| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| FR-01 | A driver can join the queue for loading or unloading from their phone, with name, plate and company. | Must | **Yes** | Built (Week 3) |
| FR-02 | A driver can see their ticket number, status and how many trucks are ahead of them. | Must | **Yes** | Built (Week 3) |
| FR-03 ★ | A driver can see the bay and arrive-by time when they are called. | Must | **Yes** | Built (Week 3) |
| FR-04 | A driver can leave the queue before being called. | Should | **Yes** | Built (Week 3) |
| FR-05 | Staff can see the waiting list, filtered by service. | Must | No (reads tickets) | Built (Week 3) |
| FR-06 ★ | Staff can call the next truck, or several selected trucks, and give each a bay and an arrive-by time. | Must | **Yes** | Built (Week 3) |
| FR-07 | Staff can mark a truck as served or no-show. | Must | **Yes** | Built (Week 3) |
| FR-08 | Staff can see how many trucks are waiting for each service. | Could | No (computed from tickets) | Built (Week 3) |
| FR-09 | A driver can confirm (OK) a finished ticket, and see it under My tickets. | Should | **Yes** | Built (Week 3) |
| FR-10 | Staff can view finished tickets in an archive and delete one. | Should | **Yes** | Built (Week 3) |
| FR-11 | Staff can add, rename and switch off a service. | Must | **Yes** | This week |
| FR-12 ★ | Staff can see how many trucks left or were no-shows, per service, per day. | Should | No (computed from tickets) | Later |
| FR-13 | A driver can switch the page to a larger text size. | Could | No | Later |
| FR-14 ★ | A driver can choose a vehicle type (4-wheeler, 6-wheeler, 8-wheeler, 10-wheeler, other) when joining, and staff can see it on the dashboard. | Should | **Yes** | This week |


★ = specific to the loading-bay setting.


## Non-functional requirements


| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | No ticket is lost when the server or the database restarts. | Reliability | Must |
| NFR-02 | Two trucks never get the same ticket number, even if they join at the same moment. | Data integrity | Must |
| NFR-03 | A truck cannot be in the queue twice at the same time. | Data integrity | Must |
| NFR-04 | A first-time driver can join the queue in under 30 seconds, with no account. (Usability test: 5 seconds.) | Usability | Must |
| NFR-05 | A driver's status and bay update on their phone within 10 seconds of staff calling them, with no page reload. | Performance | Should |
| NFR-06 | The app works on a budget Android phone in sunlight, on screens as small as 360 px wide and on slow mobile data. | Compatibility | Must |
| NFR-07 | Every screen scores 90 or higher in the Lighthouse accessibility check. | Accessibility | Must |
| NFR-08 | The app collects only driver name, plate, company and vehicle type, and no password or secret key is stored in the repository. Staff pages will require login (Week 11). | Security / privacy | Must |


## MVP


**MVP:** FR-01 to FR-04, FR-06, FR-07 and FR-11, with NFR-01 to NFR-03. A driver can join, see their place and
the bay and time when called, and leave. Staff can call and serve trucks and manage the services, and no
ticket is lost or duplicated. This is the smallest version that solves the problem, because it removes
the not-knowing and lets drivers wait away from the gate while keeping the queue fair.


**Out of scope this semester:**
- SMS or push alerts when a truck is called, because they need a paid messaging service; drivers open the page to see their status.
- Staff login and roles, because they come in Week 11; the staff pages are open until then.
- GPS or automatic detection of arrival, because it needs extra hardware; staff mark arrival and no-show by hand.
- Booking future time slots, because DockQ is a live queue and appointments would change the data design.


## Checked with a real person


Checked on: [date]   Way: [in person / chat]


| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
| Dispatcher | Suggested adding a vehicle type, such as 4-wheeler, 8-wheeler and others. | Added FR-14 ★ (Should). The type is stored on the truck, so the schema gets a `vehicle_type` column. |
| Truck driver | It is all goods, so cargo does not matter to him. His only concern is where he goes and what time. | Kept FR-03 (bay and arrive-by time) as a Must and ranked it first. Did not add a cargo field, because he said it is not needed. |
