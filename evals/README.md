# A/B test

Three prompts, each run once **with** the skill and once **without** it, then graded by `grade.py` on 12–13 objective checks.

| Eval | Prompt (from `evals.json`) | Result with / without |
|---|---|---|
| `menubar-monitor` | SwiftUI macOS menu bar temperature monitor with a Settings window | 12/12 · 10/12 |
| `web-dashboard` | Apple-style single-page service status dashboard (HTML) | 12/12 · 9/12 |
| `review-bad-code` | Review and fix `inputs/BadSettings.swift` | 13/13 · 13/13 |

## Reproduce
1. For each eval, run the prompt in two fresh Claude Code sessions: one with `hig42-design` installed, one without any design skill.
2. Save outputs to `evals/iteration-1/<eval>/with_skill/outputs/` and `…/without_skill/outputs/`.
3. `python3 evals/grade.py iteration-1` (needs a Mac with Xcode; some checks type-check Swift).

## Caveats
Three prompts, one run each, checks written by the author. Treat the numbers as a direction, not proof. More prompts, repeated runs and independent graders are welcome — see `CONTRIBUTING.md`.
