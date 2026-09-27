# The confidence score that could never say "high"

*A Cairn Signals case study. The product is a production RAG SaaS, anonymised. September 2026.*

## What the product showed

Every answer came with a confidence percentage and a band: low, medium or high. Answers
were grounded in the customer's documents, cited, and checked. Confidence regularly sat in
the 60s, sometimes the low 70s, and it looked plausible: a careful system being modest.

## What was actually happening

The confidence scorer combined several factors. Five of them were read from each chunk's
metadata: `enhanced_chunking`, `context_summary`, `confidence_indicators`, `document_type`
and `similarity`. The ingest pipeline wrote none of them. Each of those factors sat at its
default on every answer, so displayed confidence topped out at about 72%, and the "high"
band starts at 80%.

For months, no answer could be rated high, however good it was. Nothing threw an error.
Code review couldn't see it either: the reader looked right, and the missing writer was in
a different part of the pipeline.

## How it was found

By working backwards from the number, not forwards from the code:

1. **List the numbers people trust.** The confidence badge on every answer was one.
2. **For each input, find the writer, not the reader.** Five fields had readers and no
   writers anywhere in the repository.
3. **Ask what happens when the input is missing.** Each missing field fell back to a
   neutral default, which is why the score looked plausible rather than broken.

The scanner's `reader-no-writer` check now finds this pattern in seconds. It lists every
metadata field that is read somewhere and written nowhere. The skill then turns each hit
into a verdict by reading the scorer.

## The lesson

> A field is done when something fails if it isn't written, not when something reads it.

A scorer returning 65% looks exactly like a scorer that works. The fix wasn't a better
formula. It was one assertion per input: fail if the writer doesn't exist.

The same audit found four more numbers of the same kind in the same product:
- a cost meter that calculated correctly and saved nothing, because tracing only ran in
  debug mode;
- a public benchmark advertising four times the cases that could actually run;
- a retired model id failing silently into a fallback;
- a "0 pending" that was really a failed query.

None of them threw an error.

**Principles:** [3. Readers need writers](../PRINCIPLES.md#3-readers-need-writers),
[4. Swallow, don't silence](../PRINCIPLES.md#4-swallow-dont-silence).
**Plugin:** [Cairn Signals](https://github.com/nicuk/llm-silent-failure-audit).
