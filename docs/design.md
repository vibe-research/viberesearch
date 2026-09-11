# How the research memory works

Vibe Research separates a small, current working set from a growing evidence record. A new session learns what matters now, then follows task-relevant links. These workflow conventions do not guarantee that an agent will remember or execute instructions perfectly.

## Two kinds of memory

The working set is edited for present usefulness. Its normal startup budget is:

| File inside `agent-research/` | Purpose | Word budget |
| --- | --- | ---: |
| `STATE.md` | Current question, status, active work, unresolved risks, next action, links | 350 |
| `docs/project.md` | Scope, goals, constraints, vocabulary, success criteria | 500 |
| `methodology/current.md` | Current method pointer, brief rationale, effective scope | 200 |
| `handoffs/LATEST.md` | Most recent checkpoint, unfinished work, resume instructions | 350 |

That is at most 1,400 words of project bootstrap content, before task-specific reads and agent instructions. Word budgets are a maintenance convention, not an exact token limit. Keep summaries within budget by removing superseded detail and linking to durable records, not by dropping unresolved risks or inventing compression certainty.

The evidence record grows as the research earns it. Historical observations, executed protocols, and consequential decisions are preserved; later corrections are explicit. An experiment file may evolve while planning. Once execution begins, retain the executed protocol and add execution records or amendments instead of silently replacing history. Historical records can be marked superseded or invalid without being erased.

## File responsibilities

| Location | What belongs there |
| --- | --- |
| `ideas/INBOX.md` | Researcher ideas, questions, and speculative directions |
| `reviews/OPEN.md` | Open comments, agent responses, and resolution status |
| `experiments/INDEX.md` | Experiment IDs, titles, status, relationships, evidence links |
| `experiments/exp-001-slug.md` | A major question or comparison and its execution records |
| `experiments/exp-001.001-slug.md` | A scoped variant of that major experiment |
| `methodology/m-001-slug.md` | A fixed method version referenced by experiments |
| `reports/` | Findings worth a separate reviewable narrative |
| `docs/decisions.md` | Optional record of consequential choices and rationale |
| `handoffs/` | Current checkpoint and useful milestone archives |

Create optional files and folders when they carry information. A discussion can update one idea and one next-action line; it need not produce a report, experiment, decision, and handoff archive. Repeated executions belong to an existing experiment when they test the same protocol. Create a child for a meaningful controlled variant and a new major number for a changed question or incompatible comparison. Never reuse IDs.

## Methods, claims, and summaries

`methodology/current.md` points to the method currently recommended for a stated scope. Write a new method version before changing that pointer. Each experiment retains the version actually used; updating current guidance does not relabel historical execution. A draft can change until fixed for use; a fixed version receives a successor, not a silent substantive edit.

State, handoffs, and reports are derived views. The evidence lives in linked sources and execution artifacts. When they disagree, inspect those sources and propagate a correction through affected summaries. A user may change the research direction immediately; a user preference does not retroactively change measurements. Record unresolved disagreements rather than smoothing them away.

## Collaboration and session boundaries

Treat researcher-written ideas and comments as human-owned text. Give comments stable IDs and a target report revision and section. Append agent responses separately. Preserve the reviewed revision when revising a report, so the comment's meaning remains recoverable. A Markdown snapshot stays beside the report to preserve relative links; mark it `Record-role: historical-snapshot` and link its `Canonical-record` so copied comments are not mistaken for new feedback. An agent can mark a change addressed with a link; it cannot invent researcher approval. Retain unresolved comments in the working set; move resolved discussions out only with a recovery link.

After a meaningful exchange, save new decisions, constraints, ideas, evidence, and next actions in their owning files, then refresh affected pointers. Avoid duplicate transcripts. Checkpoint before long operations, before compaction when possible, and after material results. An interrupted session may stop before its final save: record job IDs, artifact paths, and how to inspect or resume unfinished work early. A Markdown instruction is not an automatic background hook.

Use one writer for shared state, indexes, IDs, and method pointers. Parallel agents can investigate separate questions and return proposed changes; the coordinator reconciles them. Save durable records before pointing summaries at them, then check links and statuses. If interrupted midway, inspect the actual records before trusting the checkpoint.

## Privacy and durability

The tracked repository contains reusable instructions and templates. Project-specific memory lives in the gitignored `agent-research/` folder. Ignore rules prevent ordinary Git inclusion; they do not encrypt files, remove already tracked content, provide backups, or share research with collaborators. Choose a separate backup or synchronization policy when needed. Preserve large artifacts in an appropriate store and keep portable references in the Markdown record.
