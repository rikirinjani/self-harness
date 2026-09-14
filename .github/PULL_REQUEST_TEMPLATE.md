## Summary
<!-- One sentence: what does this proposal change in the harness? -->

## Related Weakness
<!-- Link to the Weakness Report this addresses (e.g., "WEAKNESS #3") -->
Weakness: ___

## Proposal ID
<!-- Leave blank — will be assigned by repo maintainer -->
Proposal ID: ___

## Harness Surface Modified
<!-- Which part of the harness does this edit target? -->
- [ ] AGENTS.md — agent role definition
- [ ] Skill file — skill instructions or workflow
- [ ] Subagent prompt — agent type system prompt
- [ ] Workflow rule — orchestration or validation step
- [ ] Tool permission — add/restrict tool access
- [ ] Other: ___

## Current State (old_value)
<!-- What does the harness currently look like? Paste the relevant section or describe. -->

## Proposed Change (new_value)
<!-- What should it become? Be specific. If it's a prompt change, show the old vs new diff. -->

## Expected Benefit
<!-- Concrete, quantified if possible. "This will reduce fixer test-breakage rate by ~30% based on 10 observed failures where 7 involved test regression." -->

## Risk Assessment
<!-- Honest about downsides. What could go wrong? What tasks might degrade? -->
- Risk level: [low / medium / high]
- Worst-case outcome:
- Rollback plan:

## Evidence
<!-- Which failure traces or weakness clusters support this proposal? Link to specific records if possible. -->

## Validation
<!-- Has this been tested in any way? Benchmark results? Shadow mode? -->
- [ ] Validator benchmark run (attach results if available)
- [ ] Shadow mode comparison (20+ equivalent tasks)
- [ ] Not yet validated — needs human review first

## Constitutional Compliance
<!-- Confirm this proposal does not violate the Constitution -->
- [ ] C-01 (Constitution immutable): Not modifying constitution.md
- [ ] C-02 (Human approval): Seeking human approval via this PR
- [ ] C-03 (Validator independence): Not modifying validator
- [ ] C-04 (Benchmark integrity): Not modifying benchmarks
- [ ] C-05 (Rollback): Rollback verified — `git revert` will undo this change
- [ ] C-06 (No weakening): This change does not reduce protections
- [ ] C-07 (Blind judgment): Open to blind evaluation

## Checklist
- [ ] All required fields above are filled
- [ ] I have read and respect the [Constitution](../blob/main/constitution.md)
- [ ] This proposal targets a specific failure mechanism, not a general rewrite
- [ ] The change is minimal — only the surface needed to address the weakness
