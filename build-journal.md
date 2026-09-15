# Four-Ball: From Idea to Clickable Prototype

*A concise decision log and build journal · September 2026*

## The starting problem

A golfer reserves a **tee time** for up to four players before friends have committed. The organizer may pay everyone’s greens fees upfront, then chase replies, collect reimbursements, and release unfilled spots before the course’s cancellation deadline.

The original idea combined booking, invitations, payments, spot sharing, and—with player consent—better user data for courses about who actually plays. We narrowed that ambition into a small interface for reviewing a reservation’s group status.

## How to read this journal

A **prompt** is an instruction or question given to the AI. A **skill** is a reusable set of working instructions; we used the **idea-refinement skill** to explore the problem and the **incremental-implementation skill** to build and check small pieces.

The quoted prompts below are selected excerpts from the conversation. Decisions and results are summarized, rather than reproducing the entire exchange.

## The workflow

### 1. Explore before prescribing

**Prompt:** “Help me refine this idea.” Later: “go back a step, i want to utilize the idea-refinement skill first to flesh out this idea”

The AI initially jumped toward a product direction. The user redirected it to ask about actual outings, who experienced the problem, and what success would feel like. The intended outcome was less stress around booking, paying, and organizing friends.

**Result:** A clearer problem grounded in the organizer’s experience, rather than an assumed feature list.

### 2. Find the specific source of stress

**Prompt:** “the biggest source of stress is not necessarily finding enough players, it's getting my preferred friends and players to confirm in time”

We explored six approaches: a shared round page, firmer commitments, deadline assistance, pre-organized groups, a wider player network, and course-supported group booking. The user favored the shared page, confirmations, and deadline assistance.

**Decision:** Give preferred friends the first opportunity to join, while leaving time to invite others or release spots before the course’s cutoff. A friend-response deadline and a course-cancellation deadline serve different purposes.

### 3. Separate acceptance, priority, and payment

**Prompts:** “I wouldn't want their invitation to expire” and “If they tapped ‘I'm In’ but haven't paid, I'd consider it filled.”

The resulting rules were:

- After the preferred response window, the organizer may invite a wider circle.
- Original invitations remain valid while space remains.
- Acceptance confirms a player; payment is tracked separately.

The user clarified that fronting the money was a financial burden, not evidence that unpaid friends were unreliable.

**Decision:** Do not require payment to confirm a spot.

### 4. Establish what is enough to validate

**Prompt:** “I would still use it regularly” — in response to whether coordination alone would help, even with upfront payment and later Venmos.

**Decision:** Start with group coordination attached to an existing reservation. Defer booking integrations, financing, public spot resale, automatic cancellation, and course-data products.

**Output:** Idea and validation scope, saved after the user requested a Markdown file. It records the proposed minimum viable product, assumptions, exclusions, and unanswered questions. One person’s stated interest supported a test; it did not establish market demand.

### 5. Build one part of the journey

**Prompt:** “use the incremental-implementation skill to create a POC of one feature within the whole, end to end”

The user approved **an invited friend claims a spot, and the organizer sees the updated group**. The AI implemented and checked successive pieces: saved confirmations, capacity and invitation rules, then the interface and walkthrough.

**Output:** An initial working application with invitation links, organizer and guest views, and SQLite—a small local database. Checks covered unpaid confirmation, repeated clicks, and two people trying to claim the last spot.

### 6. Correct an oversized prototype

**Prompt:** “The prototype should be simply one screen with two or three states, max.”

The first implementation had too much interface and explanation. The user specified that context belonged in accompanying documentation and the screen should feel like a small piece of an existing product.

**Decision:** Replace the dashboard and scenario controls with one invitation card: invited → confirmed. Add a single HTML file that teammates could open without installation.

**Result:** A simpler review artifact. The scope moved toward a clickable interface experiment; the earlier server code remained available separately.

### 7. Switch to the organizer’s perspective

**Prompt:** “I'd like to have the view from the organizer's POV instead of from the invited player.”

**Result:** A compact reservation card showing confirmed players and open spots. Its initial action copied an invitation for sharing in a group text. This intermediate version tested the organizer’s understanding of availability and sharing.

### 8. Show the reservation’s progression

**Prompt:** “see the open spots when they initially book, then a pending state after invitations are sent, then a full group state”

**Decision:** Keep one screen, but show three stages:

| Stage | What the organizer sees |
| --- | --- |
| Open | Organizer confirmed; three available spots |
| Pending | Three named invitees awaiting replies; still only one confirmed player |
| Full | Four confirmed players; friends’ payments remain pending |

**Result:** Scripted clicks demonstrate the progression. Sending an invitation never increases the confirmed count by itself.

### 9. Refine wording, branding, and replay

**Prompts:** “Change the header to ‘Manage your round’”; “Create a small ‘reset prototype’ link”; “Let's call it ‘Four-Ball’.”

The user rejected the initial First Dibs name and then Roundmates, requested naming options before further changes, and selected **Four-Ball**. We retained the four-dot icon and added an otherwise empty application header for future navigation.

Other refinements removed the organizer label above the card, renamed “Check responses” to **Nudge your friends**, and added reset behavior. Sample players became Ben Pardee, Tiger Woods, Rory McIlroy, and Nelly Korda; the course became Bethpage State Park - Black Course. 

**Result:** The current branded, replayable prototype.

### 10. Consolidate the deliverables

**Prompts:** “Update all of our source file names” and “clean up the folder so there's only the most recent versions”

The source folder and packages were renamed to Four-Ball. Superseded names and duplicate prototype files were removed. The retained HTML and ZIP were checked against the current source.

**Outputs:** Clickable prototype, source package, and implementation notes. The editable source lives in `four-ball-poc/`.

## What the final prototype proves—and what it does not

The current HTML demonstrates three group states and a reset action. Automated interface checks verify the transitions, player counts, pending versus confirmed labels, and deferred payment. Earlier database checks verified actual saved confirmations and capacity protection. Real-browser visual verification was limited by the available tooling.

**The final mockup does not send invitations, retrieve replies, collect payment, or save changes.** “Nudge your friends” advances to a scripted full group for demonstration; a real reminder would not confirm anyone. The earlier server/database implementation remains in the source package but is not used by this screen.

## The repeatable lesson

Describe a real situation → explore alternatives → decide the rules → choose one small interaction → build → critique the result → simplify → check → package.

The most useful prompts supplied concrete corrections: whose perspective to show, how many states to allow, what an acceptance means, and what to remove. The next step is to watch unfamiliar teammates use the prototype without coaching, then test whether the underlying coordination approach reduces chasing across real outings.
