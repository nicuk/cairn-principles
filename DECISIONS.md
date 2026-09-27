# Design decisions

Each decision records what was chosen, what was rejected, and why. A decision is changed
by adding a new entry that supersedes it, never by editing the old one.

---

### D1. A script locates, the model judges

**Chosen:** each plugin pairs a deterministic script (regular expressions and an import
graph, no model calls) with instructions that tell Claude how to turn each hit into a
verdict by reading and running the code.

**Rejected:**
- *A full AST analyser per language:* precise, but a separate parser for every language
  and framework, and it still can't judge intent ("is this `0` a real zero?").
- *Model-only:* flexible, but not repeatable. Two runs can disagree, and on a large repo a
  model reading files one at a time misses what a graph finds in a second.

**Why:** the script makes the check the same every time and scales it; the model supplies
the judgement. Every script output says it is a locator, not a verdict.

### D2. Read-only, no network, enforced

**Chosen:** every script only reads files and runs read-only `git` commands. CI fails the
build if a networking module is imported.

**Why:** these plugins read people's code. "We don't send anything" is a claim, so it gets an
enforcer (principle 1). It also makes the directory's data-handling answers true by
construction: no personal data read, nothing sent, nothing kept.

### D3. Every check is made to fail before it ships

**Chosen:** each script has a `--self-test` that plants one defect per check in a temporary
folder and confirms each check fires. New checks, and fixes to false positives, also get a
planted case, and each case is proven by reverting the fix once and watching the self-test
fail.

**Why:** a check that has never failed has never been tested (principle 6). Building these
plugins hit that repeatedly: scripted edits that "succeeded" and changed nothing, and a
verification that passed because it matched the wrong text.

### D4. Fail only on breaches; warn otherwise; fix false positives with a guard

**Chosen:** severity levels (FAIL and WARN; or HIGH, MEDIUM and INFO). When a real run
produces a false positive, the fix comes with a self-test case built from that real input.

**Why:** a check that cries wolf gets switched off (principle 8). Verify's first real run
accused an honest commit six times; each accusation became a regression case.

### D5. Publish every result, including the nulls

**Chosen:** results are reported with their size and their limits. When the with/without
comparison showed no accuracy gain (Verify on small apps), that went in the README.

**Why:** the family's premise is that unenforced claims rot. Overclaiming its own results
would contradict it.

### D6. One repository per plugin, one shared style

**Chosen:** each plugin has its own repository, because the directory requires each plugin
to be self-contained and users install them separately. The generator for visuals, the
palette, the icon and the README structure are shared by copying.

**Rejected:** a single repository holding all three, which makes one plugin's listing
depend on another's history.

**Consequence:** copies can drift. A check that the shared parts stay identical is planned.

### D7. Searchable repository names, distinctive plugin names

**Chosen:** repository names say the pain (`did-ai-really-fix-it`), for GitHub search.
Plugin names are `cairn-<name>`.

**Why:** `claude-md-management` is Anthropic's own plugin name, so the directory blocks it,
and a name made only of generic words gets held for review.

### D8. The icon is a file, not a manifest field

**Chosen:** `.claude-plugin/icon.svg`, which the directory finds by file name, drawn from the
same vector stones as the banners.

**Why:** an `icon` field in `plugin.json` draws an "unrecognised field" warning, because
Claude Code itself doesn't read it.
