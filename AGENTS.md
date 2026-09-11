# Working on Vibe Research

This repository distributes a research workflow. Its tracked documentation and
examples describe the product; they are not findings from a live research project.

- The installable research instructions are
  `.agents/skills/vibe-research/assets/AGENTS.md`. The matching skill entrypoint is
  `.agents/skills/vibe-research/SKILL.md`. Keep these roles separate: the bootstrap
  routes a new session; the skill contains the working procedure.
- Keep the default working set small. Add a file only when it has a distinct
  reader, source of truth, or lifecycle. Create optional research records lazily.
- Preserve existing project instructions and all researcher data on installation.
  Never force-add `agent-research/`, overwrite evidence, or treat ignored files
  as backed up. Keep examples unmistakably fictional.
- Changes to file names, CLI behavior, or templates must agree across the skill,
  installer, README, walkthrough, and tests. Use Python 3.10+ and the standard
  library for the helper; no runtime package installation is needed.
- Run `python3 -m unittest discover -s tests -v` for behavior changes. Exercise
  installation and a fresh-session context export in a temporary directory when
  changing templates or bootstrap behavior. Validate local documentation links.
- Evaluate substantial workflow changes with a realistic fresh-session scenario:
  a pivot, contradictory results, an interrupted run, or unresolved human feedback.
  Structural checks alone cannot establish scientific quality.
- Use explicit paths when reading ignored state; ordinary repository searches
  may skip it. If this repository has an initialized `agent-research/`, use its
  bootstrap only for actual research tasks, not to invent research notes about
  routine framework maintenance.
