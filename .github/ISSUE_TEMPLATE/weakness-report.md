---
name: Weakness Report
about: Report a recurring agent failure pattern for the Weakness Miner
title: 'WEAKNESS: [Agent] — [short description]'
labels: weakness
assignees: ''
---

## Agent
<!-- Which agent exhibited the failure pattern? -->
- [ ] explorer
- [ ] fixer
- [ ] designer
- [ ] librarian
- [ ] oracle
- [ ] observer

## Failure Pattern
<!-- Describe what goes wrong. Be specific — what does the agent do, what should it do instead? -->

## Frequency
<!-- How often does this happen? Every time? ~50%? Rare but costly? -->

## Evidence Count
<!-- How many times have you observed this? -->
- Observations: ___

## Example Trace Summary
<!-- Walk through one representative failure. What steps did the agent take? Where did it go wrong? -->

## Verifier Signal
<!-- How do you know it failed? Test failure? Wrong output? User correction? Error message? -->

## Severity
- [ ] Critical — data loss, destructive action, security violation
- [ ] Major — task failure preventing objective completion
- [ ] Minor — reduced quality or efficiency
- [ ] Cosmetic — formatting or presentation

## Failure Category
- [ ] Tool failure — wrong tool, wrong usage, tool error
- [ ] Workflow failure — wrong process, skipped step, wrong order
- [ ] Reasoning failure — wrong conclusion, missing logic
- [ ] Configuration failure — wrong settings, missing config
- [ ] Communication failure — unclear output, wrong audience

## Suggested Harness Surface (optional)
<!-- If you know which part of the harness could address this, suggest it:
     system prompt, tool permissions, workflow rule, verification step, etc. -->

## Environment
- Harness version: ___
- Model (if known): ___
