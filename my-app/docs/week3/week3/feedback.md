## Screen 1: Join the queue

**Works well:** The form has only four fields (driver name, plate, company, service) with large
inputs and one full-width "Get a ticket" button. This follows Ramon's rule that he types little,
one-handed, in a cab. Errors show in text under each field and keep what he typed.

**Problem:** The plate rules (capital letters, numbers, spaces and hyphens, 4 to 12 characters) only
appear after a failed submit, and the service dropdown says "Loading or unloading?" without saying
what each means. This breaks *error prevention*: a driver in sunlight finds out the format only by
getting it wrong.

**Change:**
- Keep the plate field forcing capitals as the driver types.
- Show a clear placeholder and keep the two service names as plain words, "Loading" and "Unloading".
  
---

## Screen 2: My Ticket

**Works well:** The ticket number is the largest element, the status is a word badge ("Waiting",
"Called", "Served"), and the position reads as a short sentence such as "3 trucks ahead of you".
When called, a green box shows the bay and the arrive-by time. This follows Ramon's rule that his
number and position must be the biggest thing, and that the page updates without a refresh.

**Problem:** In my usability test the driver finished every task but did not notice that archived
tickets were behind the top-right menu button on his phone. This breaks *recognition rather than
recall*: nothing on the page said the archive existed. Also, the page does not say that it refreshes
itself, and it gives no instruction if a driver misses the call.

**Change:**
- Add a note under the ticket card saying where archived tickets are, "tap the menu button at the
  top right" on a phone.


---

## Screen 3: Staff dashboard

**Works well:** The waiting count per service is at the top, the filter is one tap, and **Call next**
is the largest button, near the top. This follows Liza's rule that the action she does most often is
the easiest one to reach. Plates are in bold, and the status uses words plus the bay and arrive-by
time.

**Problem:** Each row has its own Bay box, time box and Call button, next to Serve and No-show, and
there is also Call next and Call selected at the top. On a phone this is crowded, the small inputs
are hard to tap, and **Serve** sits right next to **No-show**, so one wrong tap moves a truck to the
archive. This breaks *error prevention*.

**Change:**
- Keep the bulk controls (Call next, tick-to-select, Call selected) above the table, and keep
  service and counter filters at the top.
- Show an empty-state message when nobody is waiting.
