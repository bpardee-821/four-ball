# Four-Ball — organizer reservation prototype

## The slice

The organizer has just booked and paid for a reservation for four players. One screen shows the reservation progressing through three states:

| State | Reservation view | Click |
| --- | --- | --- |
| Open | Ben Pardee is confirmed; three individual spots are open | Invite 3 friends |
| Pending | Tiger Woods, Rory McIlroy, and Nelly Korda are awaiting replies; still only one player confirmed | Nudge your friends |
| Full | All four named players are confirmed; friends’ payments are still pending | Group confirmed (complete) |

The course, date, time, price, and four spots stay in place throughout. Status is communicated with text as well as color. A simple Four-Ball wordmark sits in an otherwise empty header reserved for future navigation. The card is titled “Manage your round.” The UI contains no scenario selector, walkthrough, or product explanation.

## Simulation boundaries

The buttons advance a scripted prototype. **No invitations are actually sent and no responses are fetched.** “Nudge your friends” advances to the scripted full-group state for this walkthrough; in a real product, sending a reminder would not confirm anyone, and individual acceptances would drive that update. Dummy names are preselected to keep the interaction to three states; selecting friends is outside this slice.

The example assumes Ben Pardee has paid $328 for four players at $82 each. Confirming a player does not settle their payment. Bethpage State Park - Black Course and the September 19, 2026 reservation are sample data. Player names and the reservation are illustrative. Changes are not saved; use Reset prototype to restart.

The earlier Python/SQLite API remains in the source package but this three-state mockup does not use it.

## Questions for team review

- Can the organizer distinguish an available spot from an invitation awaiting a reply?
- Is it clear that sending an invitation does not confirm a player?
- Does the completed group feel complete even though friends still owe money?
- What information would the organizer need before deciding to invite a wider circle?

## Dependencies exposed

Real reservation data and available capacity; selecting and identifying invitees; invitation delivery; response capture; live roster updates; and payment status. Cancellation deadlines and widening access remain outside this narrow view. Pending invitations do not establish reserved ownership of a spot; the production claiming rule still needs enforcement.

## Development and checks

- Edit `static/index.html`, `static/style.css`, and `static/app.js`.
- Run `python3 build_standalone.py` to rebuild the single file.
- Optional DOM tests: install `jsdom`, then run `node test_ui.cjs`.
- Optional server: `python3 server.py --port 8766`.

DOM checks cover all three transitions, four fixed spots, pending versus confirmed counts, dummy names, and deferred payment. Reset behavior is checked from both the pending and full states. Visual verification in a real browser remains limited by the available tooling.
