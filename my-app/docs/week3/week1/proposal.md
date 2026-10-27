# DockQ: Project Proposal

**Name:** Sam B. Tomenio   **Student ID:** 20241845

## 1. Setting and problem
- **Setting:** Loading Bay like Pilmico
- **Problem:** The loading area has limited space and cannot accommodate all trucks at once. Drivers have difficulty determining when they should arrive because loading schedules do not always provide an exact waiting time. Since trucks cannot physically line up without overcrowding the area, drivers must remain inside their cabs or near the gate to monitor their turns. Long waiting periods also cause unnecessary engine idling, fuel consumption, and delays to subsequent trips.
- **Who is affected:** drivers (people waiting) and dock staff or dispatchers (people who serve)

## 2. Research
**Interviews** (who, role, when; no full names):
| # | Role | Date | Key findings |
| --- | --- | --- | --- |
| 1 | Truck driver | [October 24, 2026] | The limited loading area prevents trucks from lining up physically. Drivers must stay in their cabs or near the gate to know when their turn arrives. Extended waiting also increases fuel consumption and delays subsequent trips. |
| 2 | Dispatcher | [October 24, 2026] | Its hard to cope with a lot of people going about and tracking them down if they arent there |

**Observation:** [what you saw while visiting: how the line forms, how trucks are called, how long they wait]

**Real quotes:** "[quote from a driver]", "[quote from a dispatcher]"

## 3. User profiles
- **Driver:** 25-50s, uses a phone possibly with one hand as driving, waits in the cab or near the gate, often doing
  paperwork or resting. Goals: get loaded quickly, know when to come in, save fuel. Frustrations:
  no exact waiting time, must stay close to the gate, idling wastes fuel and time.
- **Dispatcher:** 25-50s, uses Phone,Laptop or Desktop at the office or gate. Goals: keep the bay busy and
  call the right truck. Frustrations: many people moving around, trucks not there when called,
  tracking them down.

## 4. Requirements
**Functional requirements** (priority: Must / Should / Could):
| ID | Requirement | Priority |
| --- | --- | --- |
| FR-01 | A driver can join the queue for loading or unloading | Must |
| FR-02 | A driver can see their ticket number and how many trucks are ahead | Must |
| FR-03 | A driver can see when and where they are called (bay, arrive-by time) | Must |
| FR-04 | A driver can leave the queue | Should |
| FR-05 | Staff can see the waiting list, filtered by service | Must |
| FR-06 | Staff can call the next truck and assign a bay | Must |
| FR-07 | Staff can mark a truck served or no-show | Must |
| FR-08 | Staff can see how many trucks are waiting per service | Could |

**Non-functional requirements:** works on a phone, readable in sunlight, loads fast on slow data,
usable one-handed.

## 5. Scope and milestones
- **MVP (this stage):** join queue, My place, staff dashboard
- **Later:** database (Week 4), REST API (Week 6), mobile app (Week 8), staff login
