# The dead auth system that took three rounds to find

*A Cairn Verify case study. The codebase is a production app of about 500 files, largely
written with coding agents, anonymised. September 2026.*

## The situation

The app had been built over months, by several agent sessions. It compiled, it
type-checked and its tests passed. It also carried a lot of code nothing used: superseded
auth plumbing, dashboards no route rendered, and a second library tree nobody had finished
deleting.

Dead code in an agent-built app isn't just clutter. It's where agents go wrong. When a bug
is reported in "the auth provider", an agent searches for `AuthProvider`, finds a file
that exports it, fixes it, sees its test pass, and reports success. If that file is the
dead copy, the bug is still there, and the next session does the same thing.

## Round by round

**Round 1.** 36 files that nothing imported were identified and deleted, after each was
checked through every channel a reference can arrive by: alias imports, relative imports,
`require`, dynamic `import()`, and raw path strings in configs and middleware.

**Round 2.** Deleting those 36 left nine more with no importers. They were an entire dead
auth subsystem (a factory, two providers, a JWT session bridge, a unified hook and its
types), kept alive only by the code deleted in round 1. None of it had been reachable from
the running app.

**Round 3.** Two more fell out.

A single pass finds only the first layer. The only way to see the rest is to repeat the
scan until nothing new appears.

## The trap: twins

The naming was the dangerous part. `components/auth-provider.tsx` exported
`AuthProvider`, and the live one was in `contexts/AuthContext.tsx`.
`hooks/use-auth-unified.ts` exported `useAuth` and `useTenant`, and the live ones were
elsewhere. Deleting by name would have removed the wrong twin and broken sign-in, which is
exactly the mistake an agent working by search makes when fixing a bug.

## What the plugin does with this

Cairn Verify's orphan scan builds the import graph and reports:
- **dead files in rounds:** round 2 is what only round 1 imports, and so on;
- **twins:** one exported name in several files, with the copy that's reachable from an
  entry point named;
- **files kept alive only by tests;**
- **files mentioned only as a path string,** such as in a config, which need a read before
  they're called dead.

Run on the same codebase later, it found every one of the 22 dead files the repo's own
guard listed, plus 10 real ones the guard had missed, in under a second. Those included a
duplicate library tree and hooks held up only by other dead components.

## The lesson

> Delete by reference, never by name. And repeat the scan until nothing new appears.

For an agent that keeps "fixing" the same bug, the first question isn't about the bug. It's
this: which copy of this code does the app actually run, and how do you know?

**Principles:** [1. Enforce, or don't assert](../PRINCIPLES.md#1-enforce-or-dont-assert),
[7. Name what would dissolve the explanation](../PRINCIPLES.md#7-name-what-would-dissolve-the-explanation).
**Plugin:** [Cairn Verify](https://github.com/nicuk/did-ai-really-fix-it).
