# Evidence

What each plugin has been tested on, what the results were (including the ones that
didn't favour it), and what hasn't been tested yet. As of 2026-09-27.

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
| **Self-test** | 22 checks, each fired on a planted defect, run in CI on every push |
| **With vs without the skill** | 93% of checks passed vs 71%, over 2 prompts (auditing a bloated memory folder; routing five facts for a new repo), 1 run each |
| **Cost of using it** | about 25k more tokens and 105 s more per task, mostly from running the audit script and checking the proposed files |
| **On real setups** | Across about fifteen real repositories and memory folders it found: indexes costing about 2,500 tokens per session; a memory the index never pointed to, so no session had ever seen it; four files each claiming to be the current direction; a one-time instruction loaded into every session for months |
| **Trigger rate** | First set: 7 of 10 prompts it should handle, 0 of 10 near-misses. The misses were narrow questions (which CLAUDE.md files load, why a rule was ignored), so the description was changed; the first fresh set then scored only 2 of 5, and after a second change a new fresh set scored 5 of 5, still with 0 false triggers |
| **`--draft-index`** | on a real 47-memory index: 10,078 bytes to 6,934 (about 2,500 to 1,700 tokens a session), every memory still linked, over-long lines 29 to 0. It did not reach the 3 KB budget, because 47 memories don't fit at one line each; merging them is left to the skill, and the script says so |
| **Not yet tested** | repositories outside the author's own (in progress) |

## Cairn Signals

| | |
|---|---|
| **Self-test** | 11 checks, each fired on a planted defect, plus separate planted cases for each `>= 0` assertion form; run in CI |
| **With vs without the skill** | 100% of checks passed vs 80% |
| **On a real product** | On a production RAG codebase of about 1,000 files, graded against an answer key written first: 5 of 5 items found with the skill, 2.5 of 5 without, including the audit's highest-impact issue |
| **Scale** | about 500 files scanned in 7.8 s |
| **Noise** | on that codebase, 101 of 157 findings were informational (68 were hard-coded model ids). The old default listed 88 findings and could hide HIGH ones behind a 25-per-check cap. The quiet default (1.1.0) lists 27, with all 15 HIGH kept and totals unchanged |
| **Trigger rate** | First set: 6 of 10 prompts it should handle, 0 of 10 near-misses. The misses were single-number questions (a "verified" badge, evals that pass on a broken prompt), where Claude went straight to the code. After a description change, a fresh set scored 5 of 5, with 0 false triggers |
| **Not yet tested** | open-source RAG apps other than the author's (in progress) |

## Cairn Verify

| | |
|---|---|
| **Self-test** | 19 checks, each fired on a planted defect, plus false-positive guards built from honest real commits; run in CI |
| **With vs without the skill** | **No accuracy difference.** Over two rounds and 8 runs, on two made-up apps built to overclaim (a fix in a dead copy, a test dropped in config, a dynamic import broken by a deletion, an unwired feature), both conditions found every planted problem. With the skill, every run also proved each verdict by running the code at each commit, gave a score, and ended with a message to paste to the agent, at about 70 s more per run |
| **On a real codebase** | On a 504-file app built with coding agents, the orphan scan found all 22 dead files the repo's own guard listed, plus 10 real ones the guard missed, in 0.6 s |
| **Precision on real commits** | Run on twelve real commits, the first version flagged 18 claims as unproven, and about half were prose ("thresholds are fixed"). After two precision fixes, 7, each a fair question. An honest deletion commit gets zero contradictions |
| **Known limit** | it can't follow an import built from a string at runtime, so the skill starts the app once before calling anything dead |
| **Trigger rate** | First set: 10 of 10 prompts it should handle, 0 of 10 near-misses. Fresh set, same description: 4 of 5, 0 false triggers |
| **Not yet tested** | a repository large enough that a model without the script plausibly misses the dead-code chain (in progress) |

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
