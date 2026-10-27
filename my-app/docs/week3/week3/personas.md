## Ramon, the driver (person waiting)

> "Lisod na gali mag hulat liny ana tawo truck pa, kapoy baya mag hulat sa liya nya nahan naka kaon tas dile ka kahawa
> pwede man ka magdala pero perwisyo man kaayo, sayang oras ba naa pa unta ka lain mabuhat sayang pud gas sa truck kami baya kasaban if kulang kay
> monitor na nila."



| | |
| --- | --- |
| **Photo or sketch** | ![Persona image](screenshots/ramon-driver.jpg) |
| **Age, role and background** | 41, truck driver who delivers to and loads at a feed-mill loading bay in Iligan City, 3-5 trips a week. |
| **Goals** | 1. Know when his turn comes so he does not have to wait at the gate. 2. Load quickly and start the next trip on time. 3. Save fuel by not idling in a long wait. |
| **Frustrations** | 1. The loading area is too small for trucks to line up, so nobody can easily leave. 2. Loading schedules give no exact waiting time, so he cannot tell when to arrive. 3. Long waits mean engine idling, wasted fuel and delayed later trips. |
| **Devices and context** | Smartphone, used one-handed from the cab, sometimes while doing paperwork or resting. Outdoors in sun glare, with mobile data that may be slow. |
| **Tech comfort** | [Low / Medium]: he uses a phone daily but should not have to type a lot or learn anything to get a ticket. |
| **Accessibility needs** | As design precautions: strong contrast for sunlight, large tap targets, little typing, short pages for slow data, and status in words, not only color. |

### Scenario

Ramon pulls up near the loading bay in the early morning with an empty truck. and it was already his turn as because before he set off to travel The
He opens DockQ on his phone, enters his name, plate number and company, chooses Loading and gets ticket #14. The page tells him "3 trucks ahead of you", so he travels and when he arrives his phone shows "Called" with a bay number and an arrive-by time, and he drives in without having stayed at the gate or asked anyone.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Join the loading or unloading queue | Join | FR-01 |
| Check ticket number and how many trucks are ahead | My place | FR-02 |
| See when and where I am called (bay, arrive-by time) | My place | FR-03 |
| Leave the queue if my plans change | My place | FR-04 |

### What this means for my interface

1. Because Ramon cannot tell when his turn comes and checks his phone one-handed from the cab, my interface must make his ticket number and trucks ahead the biggest thing on My place.
2. Because he waits away from the gate and may be resting or doing paperwork, my interface must update the status by itself and show the bay and arrive-by time as soon as he is called.
3. Because he is outdoors with slow data and may wear gloves, my interface must use few fields, large inputs and buttons, high contrast and light pages.

---

## Liza, the dispatcher (staff member)

> "It's hard to cope with a lot of people moving around, and hard to
> track them down when they aren't there."

If you have the dispatcher's exact words, replace this with the real quote.

| | |
| --- | --- |
| **Photo or sketch** | ![Persona image](screenshots/liza-dispatcher.jpg) |
| **Age, role and background** | 28, dispatcher at the loading bay who decides which truck goes in next and tracks who is present. |
| **Goals** | 1. Keep the loading bay busy by calling the right truck next. 2. Know who is waiting and who has not arrived. 3. Keep loading and unloading trucks in order without chasing people. |
| **Frustrations** | 1. Many people and trucks moving around, which is hard to cope with. 2. Tracking people down when they are not where she expects. 3. Trucks that are called but absent, which blocks the line. |
| **Devices and context** | [Office computer / tablet] at the bay office, with frequent interruptions from drivers and radio calls. She must read the screen at a glance. |
| **Tech comfort** | [Medium]: comfortable with basic office software, but she should not have to learn a complicated queue workflow. |
| **Accessibility needs** | As precautions: readable table text, clear focus states, large buttons that are hard to mis-click, and explicit messages after each action. |

### Scenario

At the start of a busy shift, Liza opens the DockQ staff dashboard on the office computer. The top shows how many trucks are waiting for loading and unloading. A bay opens, so she types the bay number and an arrive-by time and presses "Call next", and that driver's phone shows the call. When several trucks can go in together, she ticks them and uses "Call selected". If a truck does not turn up, she marks it as a no-show and the next one moves up, so she no longer has to hunt for people. When a truck finishes, she presses "Serve" and it moves to the archive with its time.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| See the waiting list, filtered by service | Staff | FR-05 |
| Call the next truck and assign a bay and arrive-by time | Staff | FR-06 |
| Mark a truck served or no-show | Staff | FR-07 |
| See how many trucks are waiting per service | Staff | FR-08 |

### What this means for my interface

1. Because Liza calls trucks all day, my interface must make "Call next" the largest button, near the top of the dashboard.
2. Because she has trouble tracking people down, my interface must show each truck's plate, status, bay and arrive-by time at a glance, with a no-show action in each row.
3. Because loading and unloading are separate lines, my interface must let her filter by service in one tap and show the waiting count per service.
4. Because she is interrupted constantly and Serve sits beside No-show, my interface must make results clear with word badges and messages, and protect against mis-taps.
