# Contributing

Make research continuity easier without making the default record larger.
Propose changes around an actual scenario: an evolving method, missing evidence,
a contradictory summary, an interrupted experiment, or researcher feedback.
Explain the failure the change prevents and what a new session should do.

The reusable workflow lives in `.agents/skills/vibe-research/`. Its `SKILL.md`
routes work; `references/` contains conditional detail; `assets/` contains the
installable project instructions and record templates. The repository's root
`AGENTS.md` describes framework maintenance. Personal study data belongs only in
the ignored `agent-research/` folder.

## Check a change

Python 3.10+ is the only runtime requirement. From this repository:

```bash
python3 -m unittest discover -s tests -v
python3 .agents/skills/vibe-research/scripts/research.py --help
```

For installer/template changes, initialize a temporary project, run `check` and
`context`, add a major experiment and a child, and confirm an existing project's
instructions and notes survive reinitialization. Tests exercise these invariants.
Do not use private research data as test fixtures.

For a meaningful workflow change, also do a fresh-session exercise: give an agent
only the bootstrap, skill, and a few raw records, then ask it to handle a realistic
pivot or contradiction. Inspect its saved files and final answer. Passing a link
checker cannot show that the agent preserved uncertainty or researcher intent.

Keep README commands, template paths, reference rules, and helper behavior in
agreement. Cite official documentation for client-specific discovery behavior.
Keep examples explicitly fictional, dependencies minimal, and human-authored text
preserved. Report only checks actually performed.

## Scope

Useful additions reduce a demonstrated failure or make existing records easier
to inspect. A new integration, service, plugin, or mandatory document should
justify its maintenance and context cost. Domain-specific rigor belongs in a
focused optional reference when it does not apply to other research.

Open an issue or pull request with the problem, proposed behavior, and relevant
validation. Remove private paths, participant data, credentials, and unpublished
results from public examples. Contributions use this repository's [MIT license](LICENSE).
