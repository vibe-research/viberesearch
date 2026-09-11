---
name: vibe-research
description: Maintain a compact, evidence-linked research workspace across sessions, including evolving questions, numbered experiments, methodology revisions, researcher ideas, feedback, and handoffs. Use for research work and substantive research discussions in a project using agent-research, or when asked to initialize this workflow.
---

# Vibe Research

Keep the researcher in the scientific conversation and the durable record ready
for the next session. The workspace is the project memory; chat is a working
surface. Preserve uncertainty and evidence when compressing that memory.

## Resume with a bounded working set

Resolve the project root from the task and repository; do not guess a different
workspace because a file is missing. Read `agent-research/STATE.md`,
`docs/project.md`, `methodology/current.md`, and `handoffs/LATEST.md` relative to
that workspace, unless already read in this session. Their respective budgets are
350, 500, 200, and 350 words. These are working-set limits, not a total token
guarantee. Read the complete relevant record when an evidential detail matters.

Reconcile the checkpoint with relevant files, repository status, and actual job
state. A timestamp or a handoff saying “running” does not prove a process is alive.
If state is stale or contradictory, inspect its linked sources before proceeding.
Prefer the user's current intent for direction and primary evidence for factual
claims. Surface unresolved contradictions; do not silently choose a convenient
summary. Never recreate lost results from memory.

Read [workspace rules](references/workspace.md) when first operating this workspace
or changing its organization. Then open only the route the task needs:

| Task | Read next | Write when something changed |
| --- | --- | --- |
| Discuss an idea | `ideas/INBOX.md`; project constraints | One idea entry; a decision only if made |
| Design or run an experiment | Active protocol; relevant experiment and baseline; [scientific method](references/scientific-method.md) | Experiment plan, then run/evidence record |
| Interpret evidence | Exact run artifacts and protocol; scientific method reference | Experiment finding; report only for useful synthesis |
| Change direction or evaluation | Current protocol, affected experiment, decision context | New protocol if substantive; decision; current pointers |
| Review a summary or report | Linked report revision and its sources; open comments | Addressed changes and replies with traceable resolution |
| Resume or hand off | Relevant checkpoint paths and actual execution state | `handoffs/LATEST.md`; `STATE.md` if needed |

Check `ideas/INBOX.md` and `reviews/OPEN.md` for new researcher input, reading open
entry sections rather than accumulating closed threads. Find inline feedback by
searching Markdown files for the exact line `Review-status: open` with an explicit
ignored-directory search (for example `rg --no-ignore --glob '*.md' -l
'^Review-status: open$' agent-research`). Load only the matching comment sections
and their targets.
Do not assume the feedback queue is exhaustive or its count is current.
Treat a copy marked `Record-role: historical-snapshot` as historical evidence:
follow its `Canonical-record` link for the live thread. Do not dismiss original
unresolved comments merely because their file is in an archive.

## Work with proportional ceremony

A short idea discussion usually needs one entry and a compact handoff. A changed
experiment needs its existing record updated. A major pivot needs a decision and
possibly a new experiment family or methodology revision. Do not generate a
report, session archive, or duplicate summary for every turn.

Before launching research, record the question, hypothesis or exploratory aim,
comparison, protocol revision, analysis plan, stopping rule, and execution scope
that matter to this study. Unknown required facts remain explicitly unknown.
Resolve only blocking gaps with the user; continue independently useful work.
Existing authorization carries forward. An idea or an item in a plan is not by
itself authorization to spend compute, access new data, or publish results.

Keep the following scientific distinctions explicit:

- Proposed, planned, running, completed, failed, and cancelled describe work.
  Observed, inferred, and untested describe claims. Neither implies the other.
- A major experiment is a question or approach; a sub-experiment is a controlled
  variation within it; a rerun is another execution, not a new hypothesis.
- A protocol describes how evidence is produced. Pin the revision in each
  experiment. A substantive method change creates a new version; it never
  silently changes the protocol behind an old result.
- Record deviations and outcome access honestly. Plans written after seeing
  outcomes are retrospective, even when they look like preregistration.
- Missing, failed, negative, null, and inconclusive results retain distinct
  meanings. A completed command is not proof of a supported research claim.

Use [record templates](references/workspace.md#record-templates) as prompts, omitting
inapplicable fields with a short reason. Link artifacts rather than embedding logs
or large tables. Preserve primary evidence and user authorship.

## Close the loop before replying

For each substantive turn, including discussions and partial progress:

1. Re-read touched sections if another person or agent could have edited them.
   One coordinator owns `STATE.md`, shared indexes, and `LATEST.md`; other agents
   return scoped findings or edit assigned experiment records.
2. Save the durable delta to its canonical record first. Include evidence links,
   unresolved uncertainty, and a dated correction or decision when applicable.
   Preserve user comments and reply below them; mark a concern resolved only when
   the requested change is verifiably addressed. Scientific agreement may remain
   unsettled after an editorial change is complete.
3. Refresh `handoffs/LATEST.md` in place with what changed, verification, unfinished
   work, exact resume instructions, and any pending human decision. Update
   `STATE.md` last if the current question, findings, active work, or next step
   changed. Do not write a transcript or repeat unchanged history.
4. Check touched links and consistency between records and pointers. Use
   `python3 .agents/skills/vibe-research/scripts/research.py check` when available;
   it checks structure, not the truth of the science. If a budget is exceeded,
   move historical detail to its owning record and retain evidence links,
   counterevidence, uncertainties, and open human concerns in the current brief.
5. Reply with the result or decision, its evidential limits, and links to changed
   records. Mention a blocker or next step when useful. Claim a checkpoint was
   saved only after the writes succeed. If writes are disallowed or fail, include
   a compact unsaved handoff in the response instead.

Checkpoint partial progress before a long run, risky transition, or expected
context loss: set `Checkpoint: in-progress` in `LATEST.md` and include the command,
job identity if known, output location, and safe recovery check. After saving the
result and state, set it to `complete`. An abrupt interruption can still lose
unsaved work; this skill is an instruction workflow, not a background hook.

## Helpers

The optional Python 3.10+ standard-library helper lives at
`scripts/research.py` relative to this skill. Use `--help` for syntax. It initializes
the workspace, allocates experiment/protocol records, checks links and budgets,
exports the bounded context, and creates local snapshots. It does not execute
experiments, judge findings, choose the next method, or auto-resolve feedback.
For manual operation, use the same files and rules. All private research content
belongs under `agent-research/`; reusable instructions and templates stay outside.
