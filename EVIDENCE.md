# Evidence

What each plugin has been tested on, what the results were (including the ones that
didn't favour it), and what hasn't been tested yet. As of 2026-09-27 (Memory and Signals 1.2.0, Verify 1.1.0).

The same rule applies throughout: a result is only reported if it could have come out the
other way.

## How the comparisons were run

Each test prompt was run twice with the same model (Claude Opus): once with the plugin's
skill and once without it. Each run had its own copy of the target repository. Answer keys
were written before any run and kept out of the runs' reach. Every run was graded against
its key, and every copy of a repository was checked afterwards to confirm it was left
exactly as found.

These tests are small: two prompts per plugin, one or two runs each. Treat them as
indicative. The fixtures and answer keys are published in each plugin repo's `evals/`
folder (see Reproducing), so anyone can re-run them.

## How the trigger tests were run

A skill only helps if Claude reaches for it. Each prompt was sent once to `claude -p` with
all of the author's installed skills competing (about 140), and the first skill Claude
invoked was recorded. Each set is half prompts that should trigger the skill and half
near-misses that belong to something else ("review my PR", "write a CLAUDE.md with the
build commands"). After a first set of 20, the descriptions were changed, then measured on
fresh prompts they weren't changed for. One run per prompt, so treat single misses as noise.

---

## Cairn Memory

| | |
|---|---|
| **Self-test** | 22 checks, each fired on a planted defect, plus 26 cases built from the false alarms real repositories produced (1.2.0), each broken once to prove it can fail; run in CI on every push |
| **With vs without the skill** | 93% of checks passed vs 71%, over 2 prompts (auditing a bloated memory folder; routing five facts for a new repo), 1 run each |
| **Cost of using it** | about 25k more tokens and 105 s more per task, mostly from running the audit script and checking the proposed files |
| **On real setups** | Across about fifteen real repositories and memory folders it found: indexes costing about 2,500 tokens per session; a memory the index never pointed to, so no session had ever seen it; four files each claiming to be the current direction; a one-time instruction loaded into every session for months |
| **Trigger rate** | First set: 7 of 10 prompts it should handle, 0 of 10 near-misses. The misses were narrow questions (which CLAUDE.md files load, why a rule was ignored), so the description was changed; the first fresh set then scored only 2 of 5, and after a second change a new fresh set scored 5 of 5, still with 0 false triggers |
| **`--draft-index`** | on a real 47-memory index: 10,078 bytes to 6,934 (about 2,500 to 1,700 tokens a session), every memory still linked, over-long lines 29 to 0. It did not reach the 3 KB budget, because 47 memories don't fit at one line each; merging them is left to the skill, and the script says so |
| **On repositories the author didn't build** | 1.1.0 crashed on one of four and none of its blocking findings was real; 1.2.0 fixed both. See [below](#on-repositories-the-author-didnt-build) |

## Cairn Signals

| | |
|---|---|
| **Self-test** | 11 checks, each fired on a planted defect, plus separate planted cases for each `>= 0` assertion form, and from 1.2.0 a must-find and a must-not-find case for each fix the open-source run needed (34 cases); run in CI |
| **With vs without the skill** | 100% of checks passed vs 80% |
| **On a real product** | On a production RAG codebase of about 1,000 files, graded against an answer key written first: 5 of 5 items found with the skill, 2.5 of 5 without, including the audit's highest-impact issue |
| **Scale** | about 500 files scanned in 7.8 s |
| **Noise** | on that codebase, 101 of 157 findings were informational (68 were hard-coded model ids). The old default listed 88 findings and could hide HIGH ones behind a 25-per-check cap. The quiet default (1.1.0) lists 27, with all 15 HIGH kept and totals unchanged |
| **Trigger rate** | First set: 6 of 10 prompts it should handle, 0 of 10 near-misses. The misses were single-number questions (a "verified" badge, evals that pass on a broken prompt), where Claude went straight to the code. After a description change, a fresh set scored 5 of 5, with 0 false triggers |
| **On repositories the author didn't build** | precision 10.9% to 37.1% and Python recall 4 of 8 to 8 of 8 after 1.2.0, but still no HIGH finding confirmed real on those apps. See [below](#on-repositories-the-author-didnt-build) |

## Cairn Verify

| | |
|---|---|
| **Self-test** | 19 checks, each fired on a planted defect, plus false-positive guards built from honest real commits; run in CI |
| **With vs without the skill** | **No accuracy difference.** Over two rounds and 8 runs, on two made-up apps built to overclaim (a fix in a dead copy, a test dropped in config, a dynamic import broken by a deletion, an unwired feature), both conditions found every planted problem. With the skill, every run also proved each verdict by running the code at each commit, gave a score, and ended with a message to paste to the agent, at about 70 s more per run |
| **On a real codebase** | On a 504-file app built with coding agents, the orphan scan found all 22 dead files the repo's own guard listed, plus 10 real ones the guard missed, in 0.6 s |
| **Precision on real commits** | Run on twelve real commits, the first version flagged 18 claims as unproven, and about half were prose ("thresholds are fixed"). After two precision fixes, 7, each a fair question. An honest deletion commit gets zero contradictions |
| **Known limit** | it can't follow an import built from a string at runtime, so the skill starts the app once before calling anything dead |
| **Trigger rate** | First set: 10 of 10 prompts it should handle, 0 of 10 near-misses. Fresh set, same description: 4 of 5, 0 false triggers |
| **On repositories the author didn't build** | measured on three outside repos: 7% precision for both `claims` and `orphans`, 6 of 7 planted overclaims found. A fix is in progress; the numbers will be published before and after |
| **Not yet tested** | the with/without comparison on a large repository (the fixture is built: outline/outline with a dead copy behind a `~/` alias and a three-deep chain) |

## On repositories the author didn't build

Everything above was measured on the author's own code or on fixtures built to show a
problem. This section is the test that could embarrass the plugins: public repositories
the author didn't write, pinned at a commit, with every finding labelled real, false
alarm or unclear from reading the code, and defects planted in copies to measure recall.
The first run found each plugin much noisier than on its home ground; each was then fixed
and measured again on the same repositories. Both runs are here.

### Cairn Memory, on four public repositories

Repositories with `CLAUDE.md`, `AGENTS.md` or `.claude/rules`: hmans/beans @99260bf,
rizsotto/Bear @7238459, juspay/kolu @e5f457c, Sage-Bionetworks/sage-monorepo @3053678.
Every finding was labelled real, false alarm or unclear, with one line of evidence each.
"Strict" counts unclear as wrong; "decided" leaves unclear out.

**What 1.1.0 did.** It crashed on kolu: a brace glob (`{website/src/**,README.md}`) in
`.claude/rules` raised an error, so that repo got no report at all. On the other three, 19
findings: 4 real, 10 false alarms, 5 unclear (21% strict, 29% decided). **None of its 4
blocking findings was real.** The false alarms had clear causes: `...` abbreviations,
placeholders like `OUT_DIR/`, gitignored build output, files the text says to create, and
folder files of 65 to 89 lines flagged against a 60-line budget that well-kept files
exceed.

**What 1.2.0 does, same repos.**

| | 1.1.0 | 1.2.0 |
|---|---|---|
| Repos audited without crashing | 3 of 4 | 4 of 4 |
| Blocking findings (FAIL) that are real | 0 of 4 | 1 of 1 (a pointer to `internal/bean/sort.go`, which moved to `pkg/bean/sort.go`) |
| All findings | 19 | 54 |
| Precision, strict | 21% | 30% |
| Precision, decided | 29% (4 of 14) | 89% (16 of 18) |
| Recall on seeded copies (22 planted defects) | 17 of 22 | 19 of 22 |
| Honest controls kept quiet | 8 of 8, but kolu's 2 only because it crashed | 8 of 8 |

Newly found and real: four stale alternatives in kolu's `.claude/rules` globs, and three
dead pointers in its agent files that 1.1.0 never walked.

**What it still gets wrong.**
- **36 of 54 findings are unclear**, almost all of them in kolu: a warning that a path
  "only resolves as" a longer one, where the sentence around it names the package in
  prose. The file exists, but whether a reader would find it is a judgement call. Nine of
  them are duplicates, because kolu generates its `AGENTS.md` from its rules and both are
  now read.
- The two false alarms left are both in a README: an example value in a table and a
  package export subpath.
- **The three missed plants are the recalibration's cost:** folder files of 75, 80 and
  90 lines no longer warn. That was a choice, made on the evidence above.
- Things it now deliberately skips can hide a real dead pointer: anything in a gitignored
  folder, a path starting with an all-caps folder, and a path in a sentence that says to
  create it. Backticked folder paths ending in `/` aren't checked yet.
- The labels were redone for this comparison, so the 1.1.0 numbers here differ slightly
  from the first informal pass (which put strict precision at 25%).

### Cairn Signals, on four open-source RAG apps

ItzCrazyKns/Perplexica @348feca, arc53/DocsGPT @420b4d3, mayooear/gpt4-pdf-chatbot-langchain
@4b2647c, zylon-ai/private-gpt @01ac43d. Every HIGH finding was labelled; MEDIUM findings
were sampled (up to 15 per repo, fixed seed). Precision is real / (real + false alarm),
with unclear findings counted separately. Recall used copies of Perplexica (TypeScript) and
private-gpt (Python) with 8 planted defects each, plus honest controls.

| | 1.1.0 | 1.2.0 |
|---|---|---|
| Precision, all labelled | 10.9% (7 real, 57 false, 15 unclear) | 37.1% (13 real, 22 false, 14 unclear) |
| Precision, MEDIUM sample | 20.0% | 44.8% |
| HIGH findings | 38: **0 real**, 29 false, 9 unclear | 16: **0 real**, 6 false, 10 unclear |
| Recall, TypeScript | 7 of 8 | 8 of 8 |
| Recall, Python | 4 of 8 | 8 of 8 |
| Controls kept quiet | all | all |

Per check (precision, all labelled): `llm-call-uncapped` 50% to 88%; `swallowed-error` 33% to
44%; `loop-uncapped` 0 of 13 to none left above INFO; `reader-no-writer` 0 of 26 to 0 of 5;
`metric-coalesce` 0 of 5 to 0 of 6.

**Why 1.1.0 was that noisy.** `reader-no-writer` read `metadata.extend(` as a field called
`exten`, and counted words in prompts and comments as reads: 18 of its 26 false alarms came
from that alone. Loops that end on a sentinel were flagged as uncapped, method definitions
as model calls, and a catch that logs on its second line as empty. Python recall was 4 of 8
because it didn't know `debug_mode`, `asyncio.create_task(...)` or `.invoke/.chat` calls.

**What it still gets wrong.**
- **No HIGH finding on these repos was confirmed real.** Nine of the 16 are `assert True`
  marker tests in private-gpt: the check is right that they can't fail, but they're
  deliberate, so they're labelled unclear. Five are `reader-no-writer` fields a library
  writes (LangChain's `metadata.source`, LlamaIndex's `_node_content`, Redux Toolkit's
  `action.meta.arg`), which no scan of the repo can see. HIGH means "serious if real",
  not "confirmed": the skill tells the reader to check each one, and these results are why.
- `metric-coalesce` found nothing real on these repos (0 of 6).
- Two new false alarms came from the fix that stopped `.get("k", default)` counting as its
  own writer. One possibly useful finding was lost: a `res.json().catch(() => ({}))` in an
  admin usage page is no longer reported.
- On the author's reference codebase, totals moved from 15/41/101 (HIGH/MEDIUM/INFO) to
  16/43/101: one new HIGH that looks real, and four catches whose body is only a comment,
  three of which are noise.
- The labels are one reviewer's, from reading the code.

---

## Reproducing

The self-tests reproduce from any clone:

```
python skills/memory-architecture/scripts/audit_memory.py --self-test      # in claude-md-memory-architecture
python skills/ai-signals-audit/scripts/scan_signals.py --self-test         # in llm-silent-failure-audit
python skills/verify-agent-claims/scripts/verify_claims.py --self-test     # in did-ai-really-fix-it
```

The with/without comparisons can be re-run from each plugin repo's `evals/` folder: a
builder that recreates each fixture, the prompts, and the answer key. Two comparisons ran
on private material and aren't published: Memory's audit prompt used a real memory folder
(the published fixture is a synthetic stand-in with the same problems), and one Signals
prompt used a private production codebase.
