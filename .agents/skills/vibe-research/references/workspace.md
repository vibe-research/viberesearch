# Workspace rules

Paths below are relative to `agent-research/`. Records are ordinary Markdown;
maintain relative links and stable IDs. Prefer meaningful names over dates alone.
Only the seven bootstrap files exist at initialization. Create other records
when they first earn their place.

## Ownership and lifetime

| File | Source of truth for | Editing rule |
| --- | --- | --- |
| `STATE.md` | Present orientation, next action, links | Replace stale working summary; at most 350 words |
| `docs/project.md` | Purpose, scope, constraints, collaboration preferences | Update on agreement; at most 500 words |
| `ideas/INBOX.md` | Researcher's proposed ideas | Preserve authored text; append agent response/status |
| `reviews/OPEN.md` | Open feedback links and general discussion | Preserve comments; archive resolved threads when bulky |
| `experiments/INDEX.md` | Experiment IDs, parents, status, one-line outcomes | One row per experiment, no run logs |
| `experiments/exp-001-slug.md` | One experiment's plan and interpretation | Freeze executed plan; append dated progress/corrections |
| `methodology/current.md` | Which protocol is active and why | Pointer plus brief change note; at most 200 words |
| `methodology/m-001-slug.md` | One protocol revision | Draft editable; once used, preserve and amend/version |
| `handoffs/LATEST.md` | Immediate continuity and recovery | Replace in place; at most 350 words |
| `docs/decisions.md` | Consequential choices and rationale | Append `D-001` entries; supersede by backlink |
| `reports/<topic>.md` | Evidence-linked synthesis for a reader | Revision/date; claims link to owning experiment/run |
| `docs/literature/<topic>.md` | Relevant sources and assessed claims | Exact citation, locator, access date, limitations |

Add a `runs/` folder under `experiments/` when executions require separate records.
Use `runs/exp-001/run-001.md`, etc. Each run records command, environment, data,
protocol, code state, result artifact locations, and status. Keep heavy outputs in
an appropriate artifact store; local ones may live under `agent-research/artifacts/`.
Record hashes and persistent locations. A local absolute path alone is not portable.
Use `artifact: /path` or `artifact: s3://...` for external artifact references;
structural Markdown checking does not verify their existence or integrity.

## Experiment lineage

Allocate major IDs monotonically: `exp-001-bce.md` (Exp 1), then
`exp-002-representation.md` (Exp 2). A within-family variation is
`exp-001.001-ce.md` (Exp 1.1); deeper levels are possible but rarely needed.
IDs are hierarchical strings, never decimals: 1.10 differs from 1.1. Do not
renumber, reuse IDs, or erase failed experiments. Use a rerun record for a new
seed/repetition with the same plan. A substantive change to the question,
population, approach, or inference target deserves a new major ID and a
`Derived from` link. Merely switching a loss can be minor or major depending on
what the comparison is intended to establish; make that rationale explicit.

Archived experiment files stay under `experiments/` and archived protocol files
under `methodology/`, with their stable basenames. The allocator scans those trees
to reserve old IDs. Move a record only when useful, update its relative links and
inbound references, and do not relocate numbered records to an unrelated archive.

Workflow: `proposed → planned → running → completed | failed | cancelled`.
Use `paused` for resumable work and retain the reason. Completion means execution
finished, not hypothesis confirmed. Track interpretation separately. Update the
index when status or interpretation changes. CLI creation starts at `proposed`;
it does not activate an experiment or declare it ready to run.

## Methodology changes

`current.md` uses `Active protocol: [M-001](m-001-baseline.md)` to select one active
revision. Use `Active protocol: none` when the method is not agreed yet. A link to
a draft elsewhere in the file does not activate it. Experiment records
link directly to their pinned revision, for example
`[M-001](../methodology/m-001-baseline.md)`, not merely to `current.md`.

Selecting a protocol identifies the current scope; it does not authorize execution
or certify that a draft is ready. Label incomplete planning explicitly. Keep
unselected alternatives outside the active field.

Edit an unused draft in place. Once used, fix typos with a dated correction; change
sampling, preprocessing, exclusions, loss definition, metric, split, analysis, or
stopping rules in a new revision. Preserve the previous method and state the
reason, effective point, comparability implications, and any outcome access.
Link successor and predecessor. Updating the active pointer affects future work;
old experiment links stay pinned. If work spans a change, split runs by protocol
and explain the deviation. A new method version need not create a new experiment
family when the underlying question is unchanged.

## Researcher ideas and feedback

The researcher may type freeform ideas into `ideas/INBOX.md`. The agent adds IDs
and responses without rewriting the original. Use `I-001` and statuses `open`,
`exploring`, `accepted`, `deferred`, or `declined`, with links when promoted.
Do not interpret a speculative idea as an approved experiment.

Comments may live in `reviews/OPEN.md` or beside a report/experiment. This format
makes inline comments discoverable even when the queue has not been updated:

```markdown
### C-001 · Researcher · 2026-09-10
Review-status: open
Target: report revision 2, section “Interpretation”

Could the improvement be due to different preprocessing?

Agent reply · 2026-09-10: The comparison is confounded. I changed the claim to
inconclusive and linked the differing configurations. A matched rerun is proposed.
Resolution: editorial correction complete; scientific question still open.
```

Use `Review-status: addressed` for a verifiably implemented change awaiting
review, `resolved` when settled, and `deferred` with a reason. Never put an agent's
words under the researcher's name. Preserve disagreement and original text;
acknowledge direct freeform edits too. Use links to exact comment anchors rather
than copying threads across files. At the start of relevant work, search for
open markers and inspect the named entry, not every historical report. Reopen a
resolved concern if new evidence invalidates its resolution.

For a reviewed report revision, keep a snapshot beside the original, such as
`reports/loss-comparison.rev-001.md`, so its relative links keep their meaning.
Add `Record-role: historical-snapshot` and a `Canonical-record` link to the live
report above the preserved body. Open-comment markers in that historical copy
are evidence of the earlier review, not new live threads. Follow the canonical
link when triaging feedback; original unresolved threads remain active even if
archived. A full-tree ZIP snapshot is another way to retain the original paths.

## Compaction, checkpoints, and recovery

The 1,400-word bootstrap budget covers only four current documents. Instructions,
feedback discovery, active protocols, and evidence require additional context.
Budgets prevent routine accumulation; they cannot ensure total token usage stays
constant. Inspect specific history when the current question requires it.

Keep each substantive fact in one owning record; summaries link to it. Compact
by moving, not discarding, provenance or unresolved counterevidence. Give moved
material a stable link and preserve old anchors where referenced. If an inbox,
decision log, or index becomes unwieldy, move closed entries to a named archive
and leave ID/link pointers. Never truncate human comments to hit a budget. Do
not archive a file each turn: save milestone handoffs at pivots, study completion,
or explicit requests. `LATEST.md` is a recovery note, not an evidence archive.

Write underlying records, then indexes/pointers, then current summaries. A shared
workspace has one coordinator for these files; reread before merging edits.
If a checkpoint is incomplete, inspect source records and real outputs, reconcile
state, and describe what is unknown. Check an existing job before resubmission.

Because the project ignores this folder, ordinary Git commits and fresh clones do
not retain it. The helper's `snapshot` saves a local ZIP, useful before a large
compaction. It is not an off-device backup and does not include external artifacts
or a code repository. The researcher chooses a private backup/sync destination.
Never create nested Git repositories, delete history, or upload files implicitly.
For a new machine/cloud session, explicitly transfer the needed workspace and
artifact access, verify links, and do not claim continuity without them.

## Record templates

Templates live in the skill's `assets/` folder (linked relative to this file):

- [Experiment](../assets/experiment.md): one hypothesis/comparison record.
- [Methodology](../assets/methodology.md): one versioned protocol.
- [Run](../assets/run.md): execution provenance and observed outcomes.
- [Report](../assets/report.md): a synthesis with claims, evidence, and comments.
- [Decision](../assets/decision.md): a short consequential choice.

The helper expands the experiment/methodology placeholders. For manually created
records replace every placeholder; use `unknown` or `not yet run` honestly rather
than inventing values. Templates are checklists to adapt, not a demand to fill
irrelevant sections. Reports and individual run files are optional when the
experiment record alone remains clear.
