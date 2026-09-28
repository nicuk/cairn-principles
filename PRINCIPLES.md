# The Cairn principles

> **A claim with an enforcer stays true. A claim with only an author rots.**

These are principles for keeping what a system says about itself true over time. That
covers comments, docs, memory files, status pages, dashboards, the numbers a product
shows, and the report a coding agent gives at the end of its work.

Each one came from a defect that shipped or nearly shipped. The incidents stay in, because
a principle without its incident is easy to agree with and hard to apply.

## How to use these

They do nothing until something goes wrong. They're responses to specific, recognisable
failures, not a process to install.

- **Apply a principle only when you can see its trigger** in the code in front of you.
  Don't apply one pre-emptively, and don't sweep a whole repo "to be safe".
- **Use the cheapest form first.** Most fixes are one line: delete an overclaiming word,
  log a swallowed error, add one assertion.
- **Every enforcer you add must be removable in one commit, and must never fire on a state
  that is intended.** If it does, the enforcer is wrong: fix it or delete it, not the code.

> **The override rule:** if applying a principle would add more friction than the failure
> it prevents, don't apply it. This rule outranks everything below.

Each principle has four parts: **Trigger** (when it applies), **Do** (what to do),
**Cheapest** (the smallest version that works) and **Where Cairn enforces it**.

---

## 1. Enforce, or don't assert

- **Trigger:** a comment, doc, status line, memory file or UI label asserts reach or state:
  "called by", "always", "every", "verified", "wired".
- **Do:** back the claim with something that fails when it stops being true, or remove it.
- **Cheapest:** delete the word. If the claim matters, add one assertion.
- **Where Cairn enforces it:** Memory's walk test (every pointer in an agent file must
  resolve); Signals' rule that a published number carries its date, runnable case count and
  re-run command; Verify's check on proof words ("verified", "works") with nothing behind
  them.

> *Incident:* a contract was documented as "one function, two callers" and had zero callers.
> Its tests passed the whole time, because they tested the function and never checked that
> anything called it.

## 2. A test that never imports its subject can't fail for the right reason

- **Trigger:** a test named after X imports only X's dependencies, never X.
- **Do:** make sure something fails if X is deleted or broken.
- **Cheapest:** rename the test to say what it tests, or add one reachability assertion.
- **Where Cairn enforces it:** Verify flags changed tests that import none of the changed
  code; Signals flags evals and assertions that can't fail.

## 3. Readers need writers

- **Trigger:** code reads a field, table, env var or config key that it doesn't produce,
  especially across a boundary (repo and database, service and service).
- **Do:** confirm a writer exists before building on the reader. A field is done when
  something fails if it isn't written, not when something reads it.
- **Cheapest:** search for the writer once. If there isn't one, delete the reader or add the
  writer.
- **Where Cairn enforces it:** Signals' reader-with-no-writer check; Memory's orphaned-memory
  check (a file no index reads is never found); Verify's "wired, and nothing calls it".

> *Incident:* a confidence scorer read five metadata fields that nothing wrote. The dead
> inputs capped displayed confidence at 72%, below the 80% "high" band, for months. Nobody
> noticed, because a scorer returning 65% looks like a scorer that works.

## 4. Swallow, don't silence

- **Trigger:** an empty `catch`, an empty `if (error)`, or a comment where the handling
  should be.
- **Do:** keep tolerating the failure if that's right, but make it observable.
- **Cheapest:** one log line with the identifiers someone would need to act on it.
- **Watch for:** a fallback that turns into a **number**. A failed query that becomes `0`
  renders as a fact ("0 pending requests"), and a real absence and a failure need opposite
  responses.
- **Where Cairn enforces it:** Signals' checks for failures that become a believable 0 and
  errors swallowed near model or cost code.

## 5. One derivation, two callers

- **Trigger:** you're about to write a generator plus a separate checker, or a producer and
  a consumer that must agree on a format.
- **Do:** share one implementation. The checker re-derives from source.
- **Cheapest:** export the function and call it from both places.
- **Where Cairn enforces it:** Memory's rule that generated status files enforce invariants,
  not byte-for-byte copies. (The family's own visuals share one generator, copied into each
  repo because a plugin must be self-contained. A daily check fails if the copies
  drift.)

## 6. Check the instrument, not only the code

- **Trigger:** a new check passes on its first run, a scripted edit "succeeded" without
  showing a change, or a search returned exactly what you expected.
- **Do:** break the thing on purpose once and confirm the check fails.
- **Known ways an instrument agrees with itself:** shell quoting that eats backslashes, a
  replace that silently matches nothing, a stale cached build, a search scoped narrower
  than you think.
- **Where Cairn enforces it:** every plugin's `--self-test`, run in CI on every push. Each
  plugin's README states its count, and CI fails if that count and the self-test disagree.

> *Incident:* in one project, twelve times a check failed right after a change that measured
> well, and every time the check was wrong, not the product.

## 7. Name what would dissolve the explanation

- **Trigger:** you have a theory and the evidence fits it.
- **Do:** before acting, name the observation that would prove it wrong, then look for it.
- **Remember:** a search result describes where you looked, not what exists.
- **Where Cairn enforces it:** Signals and Verify require it before every verdict; Memory
  treats every stored memory as a claim about the past, checked before it's acted on.

## 8. Don't cry wolf

- **Trigger:** a check flags states that are intended, or flags most of what it covers.
- **Do:** narrow it until everything it flags is actionable.
- **Why:** people disable a signal that's usually noise, and then it's gone when the real
  case arrives.
- **Where Cairn enforces it:** Memory fails only on breaches and warns otherwise; Signals
  ranks findings HIGH, MEDIUM and INFO; Verify's false-positive guards are sentences from
  honest real commits that an earlier version wrongly flagged.

## 9. Check what a metric is defined over

- **Trigger:** you're proposing a new metric or quality measure.
- **Do:** before testing whether it works, check whether it can see the cases that matter.
- **Cheapest:** one sentence: *"This measures X. Our main failure is Y. Can it see Y?"*
- **Where Cairn enforces it:** Signals' scoring item for quality metrics.

> *Incident:* a faithfulness metric inspected the quotes inside answers. It couldn't see
> failures where no answer was given, and those were 68 of 70 failures. Four experiments
> measured it before one sentence ruled it out.

## 10. Name the narrowest verifying command

- **Trigger:** you're writing an instruction to check, confirm or apply something.
- **Do:** name the narrowest command that does it.
- **Why:** a reader who isn't given one reaches for the broadest command they know, and
  "confirm the migration is applied" becomes a push of every migration.
- **Where Cairn enforces it:** Memory's status memories carry the command that re-checks
  them; Signals and Verify give the one query or command that settles every "can't tell".

---

## What this deliberately doesn't ask for

- **No required process, dashboard or coverage target.** Each principle works at the moment
  you're already reading the code.
- **No volatile data in a checked artefact.** Keep dates, hashes and counts out of anything
  a check compares, or every unrelated commit fails it.
- **No retroactive sweep.** Fix a claim when you touch it or when it bites.
