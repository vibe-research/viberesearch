# Scientific practice

Read this reference when designing experiments, changing methods, analyzing evidence, or writing conclusions. These are project conventions for making reasoning inspectable; adapt the relevant checks to the field and the consequence of being wrong. A brief idea discussion needs a faithful note, not a full protocol.

## Match the claim to the investigation

State the research question, intended contribution, scope, and what evidence could weaken the claim. Distinguish description, prediction, association, causal inference, theory, and interpretation. A benchmark improvement does not establish a causal mechanism or general usefulness. Exploratory or qualitative research can use explicit questions and competing interpretations without inventing numerical hypotheses.

For a consequential comparison, specify:

- The comparison or credible baseline, primary outcome, practical success threshold, and relevant failure conditions.
- The unit of observation and unit of analysis; population, sampling or case-selection process, exclusions, and missing-data handling.
- The method, resources, stopping rule, and analysis plan needed to interpret the outcome.
- Plausible alternative explanations, confounders, measurement limits, and checks that could distinguish them.

“Try BCE versus CE” is an idea until the task, label semantics, comparable outputs, data, evaluation rule, and reason for comparison are defined. Do not assume both losses fit the same problem.

## Preserve prospective and exploratory reasoning

Before a confirmatory run or analysis accesses the relevant outcomes, save the protocol and identify its method version. Record when it was fixed and what data or outcomes had already been seen. A local timestamp is a planning record, not proof of independent preregistration.

Record amendments with reason, time, outcome access, and affected comparisons. Changes made after seeing outcomes are exploratory for those outcomes; describe them openly and seek fresh evidence for confirmation. Previously inspected data do not become unseen by starting a new session or experiment file. Never rewrite the original prediction to match the result.

Use a new major experiment for a changed research question or incompatible comparison; use a child experiment for a scoped variant. Numbering describes lineage, not scientific independence.

## Keep comparisons interpretable

Check whether baseline and candidate share appropriate data access, preprocessing, evaluation, tuning opportunity, and resource constraints. Record intentional differences and why they are justified. Report baseline tuning and selection procedures, not just the winning setting.

Prevent leakage across training, selection, and evaluation where those roles apply, including repeated subjects, near-duplicates, time, groups, and preprocessing fitted outside the permitted subset. Separate exploratory selection from final assessment. Repeatedly consulting a held-out result compromises its role as an untouched assessment.

For other designs, address the corresponding risks: allocation and confounding for causal claims; reflexivity, case selection, discrepant evidence, and traceable coding for qualitative work; assumptions and counterexamples for theoretical arguments. Do not impose randomization or significance testing where they do not answer the question.

For literature synthesis, record the search scope, sources, queries, date cutoff,
screening criteria, exclusions, and appraisal method as relevant. Distinguish a
selective reading list from a systematic search. Inspect the cited source and
avoid counting multiple reports of the same study as independent evidence.

## Record execution and provenance

Separate **planned**, **executed**, **observed**, and **inferred** content. A submitted job is not a completed run; successful execution is not a validated result. Keep failed, interrupted, invalid, and null-result runs visible with reasons and their effect on interpretation.

Give each execution a stable run identifier. Capture applicable provenance or explicitly mark it unavailable:

- Code commit and uncommitted changes, retained as a patch or exact snapshot; command, configuration, environment or dependency versions, hardware when relevant, and seeds or other randomness controls.
- Dataset/source version, access date where needed, inclusion criteria, split identifiers, transformations, instrument or collection protocol, and analysis version.
- Start/end or interruption status, output locations, logs, and artifact checksums when useful for identity or integrity.

Keep substantial outputs outside Markdown and link to stable, accessible artifacts. Record the storage location and any access restrictions without copying secrets or sensitive raw data. A temporary path alone is not durable provenance. Seeds alone do not guarantee reproducibility. Mark missing provenance as a limitation; never reconstruct it as if observed.

## Analyze with calibrated uncertainty

Use uncertainty estimates justified by the design and dependence structure. Do not count correlated examples, repeated measurements, or runs as independent samples without justification. Separate variation across seeds from uncertainty about a population or deployment setting. State sample sizes and denominators.

Report meaningful effect sizes, uncertainty, distributions or important subgroups, and practical tradeoffs where supported. For formal hypothesis testing, identify the family of comparisons and how multiplicity and optional stopping were handled. For exploratory searches, disclose the search and selection process; do not present the best observed result as an unbiased estimate.

Absence of a detected effect is not evidence of equivalence unless the design supports that inference. Distinguish “inconclusive,” “inconsistent with the prediction,” and “invalid measurement.” Keep negative findings and contradictory evidence available.

## Make conclusions auditable

Every material empirical claim needs an evidence link to the experiment, execution, and underlying artifact or inspectable calculation. Literature claims need the actual source and the relevant passage, section, or identifier when practical. Clearly distinguish source statements, agent interpretation, and user hypotheses. Never invent measurements, citations, successful execution, or review approval.

Reports state the question, method version, result status, evidence, interpretation, limitations, and next decision. Summaries inherit uncertainty; they cannot convert a provisional finding into an established fact. Say what was not measured and avoid claiming transfer beyond the evaluated setting.

## Correct without erasing

When evidence or analysis is wrong, append a dated correction identifying the original claim, reason, replacement, and affected descendants. Preserve the original record and mark its status. Follow explicit links to update the experiment index, current state, affected report revisions, and method guidance where necessary. If all downstream uses cannot be checked, record that remaining uncertainty.

Resolve scientific disagreement through evidence and assumptions. The researcher chooses goals and priorities; that authority does not change observed results. Keep unresolved interpretations visible until the evidence supports a resolution.
