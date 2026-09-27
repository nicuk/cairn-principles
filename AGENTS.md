---
authority: binding
status: live
---

# Cairn principles: rules for agents working here

This public repo holds the shared principles, evidence and design decisions behind the
Cairn plugins. The plugins live in their own repos: `claude-md-memory-architecture`,
`llm-silent-failure-audit` and `did-ai-really-fix-it`.

| document | role |
|---|---|
| `PRINCIPLES.md` | the ten principles every plugin enforces; change only with an incident behind the change |
| `EVIDENCE.md` | test results, including the nulls; a result goes in only if it could have come out the other way |
| `DECISIONS.md` | design decisions; add a superseding entry, never edit an old one |
| `assets/make_assets.py` | the visuals, from the palette and stones shared across the family |
| `assets/icon.svg`, `assets/cairn-logo.png` | the reference copies every plugin repo must match |
| `scripts/check_drift.py` | fails when a plugin repo's shared parts drift from the reference; runs daily |

## Rules

- **This repo is public.** Plans, internal scores, client names and anything under an NDA
  never go here. The working plan lives in a separate private repo.
- **Every number here must be reproducible, or say that it isn't.** Give each new result
  its date and the command or fixture behind it.
- **Incidents stay anonymised:** describe the kind of product ("a production RAG SaaS"),
  never the product.
