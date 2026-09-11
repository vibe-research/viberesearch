## Research workspace

Use the Vibe Research workflow for this project's research, experiment, analysis,
and research discussion tasks. Respect the user's current request and the
project's existing instructions. A read-only request stays read-only.

The private working record is `agent-research/`. At a new session or after context
loss, read these in order, using explicit paths because Git searches may skip them:

1. `agent-research/STATE.md` — current question, supported findings, active work,
   uncertainty, next action, and links.
2. `agent-research/docs/project.md` — stable purpose, constraints, and preferences.
3. `agent-research/methodology/current.md` — pointer to the active protocol.
4. `agent-research/handoffs/LATEST.md` — last checkpoint and recovery instructions.

Then read `.agents/skills/vibe-research/SKILL.md` and follow its task-specific
routing. Open the active protocol before designing, running, or interpreting
research. Retrieve the needed evidence; do not load the entire research history.
If the workspace is missing, report that state is unavailable; initialize it only
for a new project, never as a substitute for recovering an existing one.

After a substantive discussion or task, save the smallest useful durable change
before replying: update the owning record, refresh the handoff, and update state
only if current understanding changed. Preserve researcher comments and ideas in
their own words. No-op acknowledgements need no file. Never present a proposal,
queued run, plausible result, or old summary as an observed finding.

Keep `agent-research/` ignored by the project Git repository. This excludes it
from ordinary commits; it provides neither access control nor backup. Never
publish or transfer private research records without the user's authorization.
