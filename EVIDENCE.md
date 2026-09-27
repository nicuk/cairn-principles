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
indicative. Larger, public tests are the next step.

---

## Cairn Memory

| | |
|---|---|
| **Self-test** | 22 checks, each fired on a planted defect, run in CI on every push |
| **With vs without the skill** | 93% of checks passed vs 71%, over 2 prompts (auditing a bloated memory folder; routing five facts for a new repo), 1 run each |
| **Cost of using it** | about 25k more tokens and 105 s more per task, mostly from running the audit script and checking the proposed files |
| **On real setups** | Across about fifteen real repositories and memory folders it found: indexes costing about 2,500 tokens per session; a memory the index never pointed to, so no session had ever seen it; four files each claiming to be the current direction; a one-time instruction loaded into every session for months |
| **Not yet tested** | how reliably the skill triggers; repositories outside the author's own |

## Cairn Signals

| | |
|---|---|
| **Self-test** | 11 checks, each fired on a planted defect, plus separate planted cases for each `>= 0` assertion form; run in CI |
| **With vs without the skill** | 100% of checks passed vs 80% |
| **On a real product** | On a production RAG codebase of about 1,000 files, graded against an answer key written first: 5 of 5 items found with the skill, 2.5 of 5 without, including the audit's highest-impact issue |
| **Scale** | about 500 files scanned in 7.8 s |
| **Known weakness** | noise: on that codebase, 101 of 157 findings were informational (68 were hard-coded model ids). A default that collapses them is planned |
| **Not yet tested** | open-source RAG apps other than the author's; trigger reliability |

## Cairn Verify

| | |
|---|---|
| **Self-test** | 19 checks, each fired on a planted defect, plus false-positive guards built from honest real commits; run in CI |
| **With vs without the skill** | **No accuracy difference.** Over two rounds and 8 runs, on two made-up apps built to overclaim (a fix in a dead copy, a test dropped in config, a dynamic import broken by a deletion, an unwired feature), both conditions found every planted problem. With the skill, every run also proved each verdict by running the code at each commit, gave a score, and ended with a message to paste to the agent, at about 70 s more per run |
| **On a real codebase** | On a 504-file app built with coding agents, the orphan scan found all 22 dead files the repo's own guard listed, plus 10 real ones the guard missed, in 0.6 s |
| **Precision on real commits** | Run on twelve real commits, the first version flagged 18 claims as unproven, and about half were prose ("thresholds are fixed"). After two precision fixes, 7, each a fair question. An honest deletion commit gets zero contradictions |
| **Known limit** | it can't follow an import built from a string at runtime, so the skill starts the app once before calling anything dead |
| **Not yet tested** | a repository large enough that a model without the script plausibly misses the dead-code chain; trigger reliability |

---

## Reproducing

The self-tests reproduce from any clone:

```
python skills/memory-architecture/scripts/audit_memory.py --self-test      # in claude-md-memory-architecture
python skills/ai-signals-audit/scripts/scan_signals.py --self-test         # in llm-silent-failure-audit
python skills/verify-agent-claims/scripts/verify_claims.py --self-test     # in did-ai-really-fix-it
```

The with/without comparisons used private fixtures and, in two cases, private codebases.
Publishing the fixture builders and answer keys, and repeating the comparisons on
open-source repositories, is the next step.
