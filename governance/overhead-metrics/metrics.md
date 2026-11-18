# Measure and reduce orchestration overhead

## 1. Purpose and assurance boundary

Measure whether delegation, routing, compression, and skills improve delivery economics without lowering quality. Historical path coverage, trace count, model self-review, and a reported “pass” are not independent acceptance.

`measure_overhead.py` aggregates versioned JSON records from trace, failure, and QMS directories. It does not execute acceptance tests, authenticate reviewers, verify invoices, or prove correctness. Its report is descriptive, not a causal estimate.

Legacy records without the schema below are reported as unsupported, not interpreted as zero-cost successful work. Missing, malformed, conflicting, or incomplete data make comparisons provisional. Do not publish multiplier claims from a provisional report.

Use protected CI/QMS to issue acceptance records. Preserve raw records, invoices, commands, retained outputs, tokenizer inputs, and reviewer evidence outside the implementer's unilateral control.

## 2. Unit of measurement

### Experimental unit

One task is one assigned change, from release of its frozen brief until final independent acceptance or a terminal failed/abandoned decision. It includes every attempt and all assigned preparation and closeout work.

A task belongs to one arm:

- `direct`: one implementation agent, plus the same independent acceptance floor.
- `delegated`: manager plus dispatched specialists, plus that acceptance floor.

Use a unique `task_id` per experimental execution, not per retry. Use `pair_id` to connect comparable executions and `task_class` for strata. Record retries under the original task. Never discard failed assignments or reclassify them after observing results.

### Primary metrics

For a closed cohort in arm A:

- **Delivery cost per independently accepted, correct change** =
  total fully allocated cost of ALL assigned tasks in A / independently accepted, correct tasks in A.
- **Elapsed time per independently accepted, correct change** =
  sum of end-to-end task elapsed seconds for ALL assigned tasks in A / independently accepted, correct tasks in A.
- Also report accepted-task latency p50/p90/p95, failed/abandoned fraction, acceptance yield, human intervention minutes per assignment and per accepted change.

The elapsed-time ratio is a failure-adjusted burden metric, not batch wall-clock throughput. Separately retain batch start/end, concurrency, and queue measurements when comparing throughput.

Zero accepted changes means the primary ratios are undefined, not zero. An unresolved/running task censors a cohort: report it, but do not compute a final cohort primary ratio. Missing cost is unknown, never free.

### Cost and time boundaries

`total_cost_usd` includes:

1. Actual model/provider charges, including cached input, output, failed requests that were charged, embeddings, and tool requests.
2. Runner, compute, storage, and other attributable paid resources.
3. Human intervention time multiplied by a preregistered loaded hourly rate.

Track human seconds separately even when monetized. Use a fixed USD conversion policy and record its date/rate in the experiment manifest. Allocate shared subscriptions/infrastructure consistently across arms; publish the allocation rule.

The ledger must cover:

- dispatch and routing;
- briefing and repeated context transfer;
- implementation;
- synthesis/integration;
- retries and failed attempts;
- verification;
- evidence creation, QMS, memory filing, and reporting;
- context management and growth;
- human authorization, debugging, recovery, and review.

An activity is an accounting item, not necessarily a serial workflow stage. Attribute each charge and each person's time exactly once. Parallel activity durations must not be summed to estimate task latency. Invoice aggregates must not be added again on top of their component calls.

Task elapsed time runs continuously from `started_at` to `ended_at`, including queues, provider outages, locks, retries, human waits, and closeout. Do not stop the clock for inconvenient dependencies.

For every model call, `input_tokens` includes cached input tokens. `context_tokens` is the subset of input attributable to carried history, repeated briefings, tool results, and decoding instructions. It is diagnostic, NOT an additional token charge. Record output tokens separately. Context classification must be consistent across arms.

`duration_seconds` supports stage-effort diagnosis. End-to-end elapsed time comes only from task timestamps.

## 3. Independent acceptance and correctness

Freeze requirements, tests, quality rubric, and risk classification before assignment. An acceptance record must refer to the exact candidate revision, acceptance suite, retained test evidence, rationale, and a reviewer identity different from the implementer.

The acceptance floor is identical in both arms. Reviewers should be blinded to arm where practical. They independently retrieve the actual diff and raw outputs rather than trusting an implementer's summary.

A task counts as accepted/correct only if:

- it is terminal `completed`;
- its authoritative acceptance is `APPROVE`;
- tests passed, correctness checks passed, and independent review is attested;
- acceptance revision and suite match the task;
- reviewer differs from implementer;
- the preregistered post-acceptance observation window has matured.

“Correct” is operational: the frozen checks plus no disqualifying defect in that observation window. It is not universal proof.

During the observation window, append defect/failure records. At window close, issue exactly one authoritative acceptance record for the measured dataset. A rejection or correctness failure remains in the denominator's cost pool but not its accepted count.

The skeleton deliberately rejects multiple acceptance records for one task instead of guessing which supersedes another. For a revised reporting snapshot, produce an auditable normalized export with one authoritative acceptance, preserving source history elsewhere. Do not silently overwrite source evidence.

## 4. Delegation versus direct baseline

### Preregistered design

Before collecting results, freeze:

- claim definitions, primary endpoints, practical benefit threshold, and harm margins;
- task strata and recruitment rule;
- sample size/power calculation, stopping rule, exclusion rules;
- allocation/randomization seed;
- model versions, tools, permissions, concurrency/resource budgets, and pricing;
- human rate and shared-resource allocation;
- tests, reviewer process, defect severity definitions, and observation window.

Sample real, representative tasks: routine edits, unfamiliar repository exploration, integration-heavy work, ambiguous requests, test-heavy changes, and failure/recovery cases. Stratify by risk, estimated size, domain, and dependency burden. Include tasks on which delegation is expected to lose.

Use paired, isolated executions of the same frozen task when feasible. Give both arms the same repository snapshot, brief, acceptance tests, and infrastructure. Prevent cross-arm access to patches, conversations, caches containing solutions, and reviewer feedback. Randomize arm order and operator allocation.

When repeat execution would leak the solution, randomize comparable tasks within preregistered strata instead. Document the resulting weaker pairing. Task selection and acceptance criteria must not be changed after seeing arm results.

Use a pilot only for instrumentation and variance estimation; do not mix it into confirmatory results. Select a powered confirmatory sample; if a pilot has fewer than 30 pairs, label it exploratory rather than inventing confidence from its size.

### Analysis

Report intention-to-treat results, including billing failures, abandoned work, rejected changes, and recovery effort.

Report by arm and stratum:

- fully allocated quality-adjusted cost;
- failure-adjusted elapsed burden;
- successful-task latency distributions and tail behavior;
- failed/abandoned fraction and acceptance yield;
- defect/severity rates during the observation window;
- intervention minutes and context tokens;
- overhead by activity category;
- paired cost/time differences and independently bootstrapped 95% confidence intervals.

Resample task pairs, not individual calls. For unpaired experiments, use the stratified assignment unit. Retain incomplete tasks as censored; report bounds/sensitivity analysis rather than treating them as instantaneous successes.

The supplied skeleton calculates descriptive summaries and linear-interpolated quantiles. It does not calculate confidence intervals, censoring adjustments, significance, or power. Perform those analyses on the retained export before making causal claims.

Do not collapse quality into an arbitrary score that hides severe defects. The binary accepted/correct denominator is primary; publish secondary rubric scores and severity counts separately.

## 5. What would falsify the claimed multipliers?

These claims currently lack a demonstrated operational denominator. Freeze an interpretation before measurement; do not change the metric after seeing results.

### “2x” delegation efficiency

Interpret as at least a 2.0 ratio of direct/delegated quality-adjusted delivery cost under a no-worse-quality constraint. If it instead means speed, preregister elapsed burden as the endpoint and label it a speed claim, not a cost claim.

- Falsified for the sampled population if the upper 95% confidence bound on the preregistered benefit ratio is below 2.0.
- A claimed general efficiency win is also contradicted if delegation breaches the preregistered quality, severe-defect, or human-intervention harm margin.
- A point estimate below 2.0 with an interval spanning 2.0 is inconclusive, not confirmation.
- Cost ratio at or below 1.0 means no observed cost advantage.

### “5x better decision-making”

This is untestable until “better” has a fixed scale. Do not use a five-point subjective rubric as a ratio scale.

Operationalize it as, for example, at least a fivefold reduction in independently adjudicated consequential routing/implementation decision errors per fixed number of comparable decision opportunities. Define opportunities and severity before execution; adjudicators must be blinded.

- Let R = direct error rate / delegated error rate.
- Falsified if the upper 95% confidence bound on R is below 5.0.
- Zero observed errors in one small arm does not establish an infinite multiplier; use an appropriate rate interval.
- A preregistered equal-cost decision-quality benchmark can be a separate endpoint, but must not replace a failing primary endpoint.
- The skeleton does not infer decision opportunities from trace prose. Retain a separate adjudication dataset for this claim.

An undefined “5x” remains unsupported; lack of a definition is not empirical falsification.

### “67–84% token savings”

Interpret as a 67–84% reduction in full attributable target-tokenizer input per equivalent usable record, including amortized decoding instructions and any reconstruction tokens.

- Falsified as a claimed minimum on the representative corpus if the upper 95% confidence bound on token-weighted savings is below 67%.
- For a universal “every record” interpretation, one valid in-scope record below 67% is a counterexample.
- If the claim is literally a bounded population mean of 67–84%, a confidence interval entirely outside that range contradicts it; savings above 84% do not contradict an “at least 67%” claim.
- Reconstruction/semantic failure falsifies usability for the affected record; do not omit failures to improve the savings estimate.
- Character-count reductions, source byte counts, and a different tokenizer do not substantiate the claim.
- Token savings alone do not establish end-to-end cost or latency savings.

Failure to achieve adequate sample size, a usable confidence interval, or complete accounting means “not established,” not “proven false.”

## 6. Token-compression verification

1. Freeze a representative held-out corpus, including short records, long paths, Unicode, escaping, optional fields, and malformed-input handling.
2. Preserve original and compressed payloads plus hashes and exact rendering/framing.
3. Use the actual deployed model's tokenizer or provider token-count endpoint. Pin tokenizer/model version and configuration hash. If unavailable, label measurements unverified; do not substitute a character heuristic.
4. Tokenize the complete baseline representation and complete compressed representation as actually delivered. Include decoding instructions, examples, schema legends, separators, chat framing, and any reconstruction tokens attributable to the compressed format.
5. If a decoder is shared across N records, measure the real batch and amortize once across those N records. Do not claim it is “free” because it is in a system prompt; cached tokens may still incur cost.
6. Verify exact round-trip reconstruction where the format promises losslessness. Independently check preservation of all semantically required fields. For lossy formats, report field-loss rates and task-quality noninferiority; the skeleton's verified compression summary only includes lossless records.
7. Report per-record savings, token-weighted corpus savings, corpus size, failure/exclusion count, confidence intervals, and real provider cost/latency where available.
8. Compare context reuse strategies under the same multi-call workload. Include repeated decoder/context charges across calls.

Savings = 1 - sum(compressed_tokens) / sum(original_tokens).
Do not average percentages when claiming corpus-wide token savings.

## 7. Skill utilization and reduction

Emit one `skill` record per actual invocation, including failed invocations. Loading a registry entry is not an invocation.

Maintain a versioned skill inventory. For each skill, report:

- invocation count, distinct tasks, arm/stratum;
- accepted-task association and invocation failure rate;
- load/briefing token and time costs, attributed through activities;
- eligible task opportunities, routing decisions, and avoidance reasons when evaluating routing;
- defects, rework, and intervention associated with its use.

Association with accepted tasks is not a causal estimate of skill value. Use randomized ablation or matched comparisons before claiming benefit.

Review unused skills against the inventory. Investigate overlapping and negative-value skills; simplify or retire only after checking rare/high-risk applicability. Do not drop safety checks merely because they consume tokens.

The skeleton reports observed skills, invocation failures, and accepted-task associations. With `--skills-file`, it also lists inventory skills with zero use. Eligibility, causal value, and decision quality require separately adjudicated records.

## 8. Record contract

All records are UTF-8 JSON objects in `.json` or `.pm1` files, JSON arrays of objects, or one object per line in `.jsonl`. Directories are scanned recursively without following symlinks. Timestamps are timezone-aware ISO 8601.

Common required fields:

- `schema`: exactly `overhead.v1`
- `record_id`: globally unique nonempty string
- `type`: `task`, `activity`, `acceptance`, `failure`, `skill`, or `compression`
- `task_id`: nonempty execution identifier

Identical replicated records are deduplicated by `record_id`. Conflicting IDs are discarded and reported. Unsupported records and parse failures make the whole report provisional because their financial/quality impact is unknown.

### Task: one per execution

Required fields:

- `mode`: `direct` or `delegated`
- `pair_id`, `task_class`, `revision`, `suite_id`, `implementer_id`: nonempty strings
- `status`: `completed`, `failed`, `abandoned`, or `running`
- `started_at`: timestamp
- `ended_at`: timestamp for terminal tasks; null for running tasks
- `accounting_complete`: boolean attesting that all allocated activities and costs are present

Example:

    {"schema":"overhead.v1","record_id":"task-d1","type":"task","task_id":"d1","mode":"direct","pair_id":"pair-1","task_class":"routine","revision":"git:abc123","suite_id":"suite:sha256:123","implementer_id":"agent-1","status":"completed","started_at":"2026-10-01T10:00:00Z","ended_at":"2026-10-01T10:10:00Z","accounting_complete":true}

### Activity: one per non-overlapping accounting item

Required fields:

- `category`: `dispatch`, `briefing`, `implementation`, `synthesis`, `retry`, `verification`, `evidence`, `reporting`, `context_management`, `human_intervention`, or `other`
- `cost_usd`: nonhuman allocated charge, nonnegative number or null
- `human_seconds`: nonnegative number or null
- `duration_seconds`: nonnegative number or null
- `input_tokens`, `output_tokens`, `context_tokens`: nonnegative integers or null

Use explicit zero when measured as zero. Null means unknown. `context_tokens` cannot exceed `input_tokens`. Retry activities count accounting items, not necessarily retry attempts. Use a failure record per observed failure; the report does not confuse those two counts.

Example:

    {"schema":"overhead.v1","record_id":"call-d1-1","type":"activity","task_id":"d1","category":"implementation","cost_usd":0.12,"human_seconds":0,"duration_seconds":45,"input_tokens":1000,"output_tokens":200,"context_tokens":300}

### Acceptance: one authoritative record per task snapshot

Required fields:

- `decision`: `APPROVE` or `REJECT`
- `revision`, `suite_id`, `reviewer_id`, `rationale`, `evidence_uri`: nonempty strings
- `independent`, `tests_passed`, `correct`, `observation_complete`: booleans

A URI is an evidence reference, not proof that the referenced evidence exists. CI must enforce access, signatures, and reviewer identity outside this reader.

### Failure

Required fields: `reason` (nonempty string), `at` (timestamp).
Failure charges and recovery effort must additionally appear in activity records.

### Skill invocation

Required fields: `skill_id` (nonempty string), `success` (boolean).
Its costs must appear in activities and must not be billed again here.

### Compression observation

Required fields:

- `tokenizer_id`, `tokenizer_version`, `tokenizer_config_hash`, `corpus_id`, `evidence_uri`: nonempty strings
- `original_tokens`: positive integer
- `compressed_tokens`: nonnegative integer, including all attributable decoding/framing/reconstruction tokens
- `decode_included`, `round_trip_ok`, `semantic_ok`: booleans

Store these observations for ALL evaluated records, including failures. They describe measurements; they do not add billable usage to the activity ledger.

Optional skill inventory file: a JSON array of unique nonempty skill ID strings.

## 9. Running the reader

Python 3.10+; standard library only.

    python measure_overhead.py \
      --traces-dir ./self-harness/traces \
      --failures-dir ./self-harness/failures \
      --qms-dir ./self-harness/qms \
      --human-hourly-usd 75 \
      --skills-file ./skill_inventory.json

Each directory flag can be repeated. A missing directory produces diagnostics and a provisional report rather than a traceback. A missing human rate leaves labor-inclusive cost unknown whenever human time is nonzero.

Default exit status is zero after a report, including provisional reports, so exploratory reporting survives partial data. Use `--strict` in reporting CI: exit 2 if there are diagnostics, incomplete tasks, unresolved quality observations, or no tasks. This is an instrumentation-completeness check, not a merge or correctness gate.

## 10. Cadence and report template

- Every request/activity: record measured usage, costs, context tokens, and failure outcomes.
- At task close: reconcile invoices and human time; independently adjudicate acceptance.
- Weekly: inspect completeness, stage overhead, intervention burden, skill use, and compression failures. Choose one reduction experiment at a time.
- At the preregistered sample/window boundary: freeze the dataset, run confirmatory analysis, and decide whether to retain, simplify, or roll back the intervention.
- Monthly: review prices, model/tokenizer versions, inventory, and task mix. Version changed protocols; do not silently pool incompatible experiments.

Report:

    Experiment / protocol version:
    Dataset hash / period / observation window:
    Model, tokenizer, tool, pricing, and human-rate versions:
    Assignment seed / strata / sample size / exclusions:
    Missing, malformed, conflicting, or incomplete records:
    Direct vs delegated:
      Assigned / accepted-correct / failed / abandoned / censored
      Total cost and quality-adjusted cost [95% CI]
      Elapsed burden; accepted latency p50/p90/p95 [95% CI]
      Failure rate; defect counts by severity; intervention minutes
      Context tokens; category overhead; retry/failure counts
    Paired benefit ratios and quality/harm constraints:
    Compression:
      Corpus / tokenizer / decoder allocation / round-trip failures
      Weighted savings [95% CI], not character reduction
    Skills:
      Inventory / observed / unused / failures / ablation candidates
    Claims:
      2x: supported / contradicted / inconclusive / undefined
      5x: supported / contradicted / inconclusive / undefined
      67–84%: supported / contradicted / inconclusive / unverified
    Highest-cost avoidable activity:
    Proposed reduction / owner / experiment / rollback criterion:
    Evidence references and retained raw outputs:
