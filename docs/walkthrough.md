# Three sessions, one continuous investigation

This is a fictional workflow example. No training was performed and no numerical
result below is presented as research evidence. The point is to show what gets
written, what stays small, and how a fresh session finds the next step.

## Session 1: “Let's try BCE, then CE”

The researcher has a classification question and a hunch about the loss. The agent
first establishes the label/output semantics, baseline, evaluation data, and
available resources. The loss names alone are insufficient to define a fair test.

The researcher writes in `agent-research/ideas/INBOX.md`:

```markdown
### I-001 · Researcher
Status: open

Maybe CE would help. I also care about calibration, not only accuracy.
```

After discussion, the agent adds a separately attributed response. The original
idea stays intact. Agreed goals go into `docs/project.md`. The first protocol goes
into `methodology/m-001-baseline.md` and the active pointer becomes:

```markdown
# Current methodology

Active protocol: [M-001](m-001-baseline.md).
Effective scope: the initial loss comparison, once the plan is complete.
Reason: agreed baseline and evaluation procedure for this question.
```

The helper allocates records; it does not run training:

```bash
python3 .agents/skills/vibe-research/scripts/research.py new-experiment bce
python3 .agents/skills/vibe-research/scripts/research.py new-experiment ce --parent 1
```

Exp 1 lives in `experiments/exp-001-bce.md`. Its variation, Exp 1.1, lives in
`experiments/exp-001.001-ce.md`. Both link directly to M-001. A repetition with the
same plan gets a run ID under its existing experiment. The agent completes the
plan before changing `proposed` to `planned`; execution starts only within the
researcher's authorized scope.

At the end of the turn, the agent updates the experiment records, their index,
and the compact handoff. State says the comparison is planned and untested. No
results report is needed yet.

## Session 2: “Could the split be leaking participants?”

Imagine that the researcher later supplies a BCE output but no CE output. A
summary mistakenly says “CE improves the baseline.” The researcher comments
directly below that summary:

```markdown
### C-001 · Researcher · 2026-09-10
Review-status: open
Target: loss-comparison report, revision 1, claim C2

CE hasn't run. Also, could the same participant appear in both splits?
```

A fresh agent reads the four bootstrap files, then checks the comment and source
records. It corrects the unsupported CE claim. Participant leakage remains a
question until the split evidence is inspected; neither a hunch nor an old handoff
settles it. The agent preserves the original comment and adds a response:

```markdown
Agent reply · 2026-09-10: Corrected C2 in revision 2: CE is untested. The BCE
output alone cannot establish the loss comparison. Participant overlap is not
verified; the next step is to inspect split IDs before interpreting the result.
Resolution: reporting error addressed; split concern remains open.
```

The agent saves a dated correction in the affected experiment/report records,
updates their index, and removes the invalid claim from current state. If needed,
the reviewed report revision is retained in a milestone snapshot. A superseded
claim stays discoverable with its correction; it stops being current guidance.

If the researcher agrees to a participant-separated protocol, the agent creates
M-002, describes what changed and why, and records whether outcomes were already
seen. Activating M-002 changes future work. The original BCE run stays pinned to
M-001. A fair comparison under M-002 needs appropriate evidence from that protocol;
the agent does not silently compare a new method against the old result.

Whether this becomes a child experiment or a new major experiment depends on the
question. A redesigned evaluation of the same loss question can remain in that
family with explicit run/protocol separation. A pivot to learning transferable
representations gets Exp 2 and a link explaining how it arose from Exp 1.

## Session 3: “Resume from where we left off”

The next session does not reread all the chat. Its current state might say:

```markdown
# Loss study · current research state

Question: Does the loss change improve the agreed classification objective?
Known: A BCE output exists under M-001; its evaluation validity is unresolved.
CE: proposed, not run. No comparative conclusion is supported.
Uncertainty: repeated participants may cross the split; IDs not inspected yet.
Current method: M-001, pending an agreed successor after the split review.
Next action: inspect split membership and report what can be verified.
Pending review: C-001 in the loss-comparison report.
```

Real records include relative links to the experiment, protocol, report comment,
and available artifacts. The handoff adds exact paths, commands already attempted,
what access is missing, and whether a job actually exists. An unavailable dataset
is recorded as unavailable. The agent can proceed with useful review while asking
for the missing location; it cannot certify a split it has not inspected.

The researcher sees a short answer with links to the corrected summary and open
question. The research history can keep growing while this orientation stays small.

## What to say to your agent

| You want to… | Try saying… |
| --- | --- |
| Capture a hunch | “Save this as an idea; it is not a decision to run it.” |
| Start fresh | “Read the research workspace, reconcile the last checkpoint, and resume.” |
| Change the question | “We're pivoting to this question. Record why and preserve the prior findings.” |
| Prepare a run | “Plan the next experiment with a baseline and a clear interpretation rule.” |
| Check a claim | “Trace this conclusion to its actual evidence and tell me what remains uncertain.” |
| Review a report | “Address my open comments and link each change to the affected claim.” |
| Close a session | “Save the current research state and the exact next step for a fresh session.” |

For the precise file ownership and lifecycle rules, read the
[workspace reference](../.agents/skills/vibe-research/references/workspace.md).
