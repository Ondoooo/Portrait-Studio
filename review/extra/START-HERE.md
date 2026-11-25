# Additional review assignments

Use this packet alongside the one already in progress. All examples are synthetic objects. The two runnable exercises target delivery defects and isolation of an experimental workflow. The remaining briefs specify small experiments another reviewer can reproduce. Each tackles a decision we still need to make. Work can be returned one assignment at a time.

## Prompt to send

> Continue the first packet. Assign spare workers to the rows below, starting with delivery defects, ranking and experimental isolation. For each, return a runnable CPU reproducer, a failing baseline, a clean control, the evidence you used, and the smallest change the result justifies. Use generated object fixtures. Keep visual votes blind until recorded. Label claims as demonstrated on the fixture, inferred, or untested in the application. Return early with the first working result. Put each result in its own directory with its command and dependencies. If a hypothesis fails, return that evidence and stop at the timebox.

| Question | Expected result | Budget |
|---|---|---|
| [At which export stage did banding, blur or halos appear?](delivery/README.md) | A stage comparison that protects real print, texture and painted edges. | 25 min |
| [Does the evaluator select a deliverable candidate?](evaluation.md#1-candidate-selection) | A blinded disagreement case and an evaluation rule that can reject every candidate. | 20 min |
| [Can experimental settings contaminate the stable workflow?](isolation/README.md) | A failing schedule, a fix and a regression check on reopened output pixels. | 20 min |
| [Does a finish obscure a join, or does stage order create it?](evaluation.md#2-finish-and-stage-order) | A controlled comparison with and without an inherited finish. | 25 min |
| [Can the model comparison distinguish adapter failure from model failure?](evaluation.md#3-model-comparisons) | A request-to-execution trace, one positive control per route, and a fair comparison protocol. | 25 min |
| [Can a claimed improvement survive a new source and seed?](evaluation.md#4-transfer-and-cost) | A small matched test design, including fallbacks, abstentions and cost per usable result. | 15 min |
| [Did an edit target the wrong part or damage a foreground object?](operations.md#1-wrong-target-and-foreground) | A falsifiable stage attribution for a rotated case with a real crossing cable. | 20 min |
| [When is the original hidden surface unknowable?](operations.md#2-hidden-surface-ambiguity) | Two identical observable inputs with different hidden patterns, plus a reporting rule. | 15 min |
| [Can a debug folder diagnose a run using only volunteered data?](operations.md#3-debug-receipts) | A portable run receipt that catches an example bound to the wrong stage without leaking a private canary. | 20 min |
| [Would more system memory change a failed run?](operations.md#4-resource-admission) | A replay that separates host commit, device allocation and an unexecuted branch. | 15 min |
| [Which custom component is actually worth replacing?](operations.md#5-existing-tools) | One evidence-backed build-or-adopt decision with a counterexample and a measured integration cost. | 30 min |

The first packet already assigns raised-outline repair, blending, pose observations and consumers, coordinate transforms, ballot provenance, interrupted export, and review of two object boards. Reuse those results if available. For example, a correctly bound ballot establishes which image someone judged. The ranking assignment here asks whether their criteria select an acceptable result.

## Return format

At the top of each result name the decision it supports, the observable failure, the earliest stage that establishes it, and a result that would reverse the recommendation. Include the input recipe, commands, before/after measurements or visual verdicts, new test, limitations, and proposed change. For existing-tool research, give a primary source and distinguish actual execution from documented capabilities. No installation or GPU time is required to deliver useful negative evidence or an executable test.
