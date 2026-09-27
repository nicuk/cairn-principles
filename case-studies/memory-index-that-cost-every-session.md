# The memory index that cost 2,500 tokens a session, and hid an "active" plan

*A Cairn Memory case study. Two long-running project memory folders, anonymised.
September 2026.*

## The setup

Claude Code keeps a memory folder per project: one small file per remembered fact, and an
index, `MEMORY.md`, that points to them. The index loads at the start of every session;
the files load only when needed. Only the first 200 lines or 25 KB of the index are ever
read.

The design is sound. Over a few months of real use, two things went wrong with it.

## What was wrong

**The index became the memory.** Each index line was meant to be a short hook ("pricing
decision: read before quoting"). Instead, lines grew to carry the finding itself, with
numbers, caveats and next steps, some over 400 characters. One index reached 10,078 bytes,
about 2,500 tokens loaded into every session before the first message.

**The memory stopped agreeing with itself.** In the second folder:
- four separate files each claimed to be "the current direction";
- one file was listed in the index twice, with two different summaries;
- index lines said "next: build X" after the file recorded X as built;
- the file that called itself the *active* plan wasn't linked from the index at all, so
  no session had ever read it.

Any new session could pick up any of those, and redo work another session had already
closed. None of it produced an error.

## What the plugin found, and fixed

The audit script flagged all of it in under a second: the index over budget, 29 lines too
long to be hooks, the orphaned "active" file (a FAIL, because a memory the index doesn't
link is invisible), the duplicate entry, and the four competing directions.

Then `--draft-index` proposed a trimmed index for review, one short hook per memory, and
never touched the original:

| | Before | Draft |
|---|---|---|
| Index size | 10,078 bytes | 6,934 bytes |
| Estimated tokens per session | about 2,500 | about 1,700 |
| Lines too long to be hooks | 29 | 0 |
| Memories linked | 47 of 47 | 47 of 47 |

That's a 31% cut with nothing lost. It did **not** reach the 3 KB budget: 47 memories
don't fit in 3 KB at one line each. Getting there means merging related memories, or moving
a cluster into a document in the repo behind one pointer line. That takes judgement, so it's
the skill's job, not the script's, and the script says so rather than pretending otherwise.

## The lessons

> The index is a budget; its lines are hooks, not findings.

> Exactly one memory says what's current. When the direction changes, demote the old one
> in the same edit.

And the one that applies to everything here: **change a memory file and its index line
together.** An index hook that still says "next: build X" sends every future session to
build X again.

**Principles:** [1. Enforce, or don't assert](../PRINCIPLES.md#1-enforce-or-dont-assert),
[3. Readers need writers](../PRINCIPLES.md#3-readers-need-writers).
**Plugin:** [Cairn Memory](https://github.com/nicuk/claude-md-memory-architecture).
