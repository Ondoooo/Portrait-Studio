# Round two review packet

The same outline can survive two different steps of an image edit. In the first case, a blue label on a canvas pouch becomes canvas-colored, but its raised shape remains in the proposed repair. In the second case, the proposed repair is clean and feathering it into the source brings an edge back. We need independent tests and working code for both cases. A separate architecture review asks how a visible pose observation actually changes a downstream decision in a fully clothed sports illustration.

| Assignment | What to return | Timebox |
|---|---|---|
| [Raised outline in the proposal](retained-shape/README.md) | Working repair function, baseline and candidate results, and one new example that preserves a genuine fabric feature. | 30 minutes |
| [Outline introduced during blending](blend-code/README.md) | Working blend function, measured results and a new test that protects a real printed line. | 30 minutes in parallel |
| [Regional pose](regional-pose/README.md), then [how the pipeline uses pose](pose-consumers/README.md) | First record observations and unknowns on the clothed mannequin. Then trace a decision from input through delivery, propose the smallest interface change, and test what happens when a caller uses or ignores the observation. | 20 minutes for observation, 25 for architecture |
| [Coordinate transforms](engineering-tasks/coordinates/README.md) | Corrected mapper, test output, and the view that exposed the error. | 15 minutes |
| [Map texture and book outline](object-tests/README.md) | Independent visual verdicts, protected details and one check that could disprove each explanation. | 10 minutes per board |
| [Other engineering briefs](engineering-tasks/README.md) | Choose one if capacity remains. Return a reproducer for interrupted export, ballot integrity or memory sampling. | Use the stop rule in the chosen brief |

## Prompt for the reviewer

> Start with the raised-logo repair and blend assignments. If you have multiple workers, split those two, and give the regional pose and architecture reviews to the same worker in that order. Use the supplied synthetic fixtures. For each coding assignment, return your complete candidate file, separate new tests, the exact run command, and measured results before and after. Keep the supplied checker intact. For visual tasks, write your verdict before opening the fixture generator. For architecture, identify which consumers actually act on each observation, what the current evidence leaves unknown, and the cheapest experiment that would change your recommendation. Include one reason to reject each proposed change. If a task reaches its timebox, return the reproducer and the first unresolved question. Mark unexecuted code as untested. Return a ZIP with one folder per completed assignment and a short results index.

Python and NumPy are sufficient for the two repair challenges. The coordinate checker uses only the standard library. A separate blend fixture is held locally for transfer testing once code comes back.

Spare workers can take an [additional assignment](extra/START-HERE.md) while these run. The first priorities there are delivered-image defects, candidate ranking, and isolation between stable and experimental settings.
