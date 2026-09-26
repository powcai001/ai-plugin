# Minimum Practice Project

Use this template to turn a domain map into a project that exposes decisions, feedback, and failure without excessive setup.

## Contents

- Project selection test and brief
- Minimize the route
- Concept-action coverage
- Decision record
- Checkpoint pattern
- Acceptance criteria
- Failure injection
- Completion package

## Project selection test

Choose a project only if it has:

- one clear user or beneficiary;
- one core action loop that activates most essential nouns and verbs;
- an observable output;
- objective acceptance criteria;
- at least one realistic failure to inject;
- a short path from the first action to trustworthy feedback;
- a completion time appropriate to the learner, normally one to three focused sessions;
- a transfer path to a second problem.

Reject projects dominated by installation, boilerplate, data collection, or decorative features.

## Project brief

```text
Project:
Learner level:
Learning target:
Essential noun-action relationships to exercise:
User and need:
Core loop:
Observable output:
Time to first verified feedback:
Constraints:
Non-goals:
Time budget:
```

## Minimize the route

Design backward from the smallest verified performance:

1. Name the first behavior that would prove useful understanding.
2. Select one task that exercises the largest number of essential relationships.
3. Remove features, tools, and setup that do not affect that behavior or its verifier.
4. Put the first observable result in the earliest checkpoint.
5. Add time only after a mastery check reveals a specific missing relationship.

Do not claim that a short elapsed time proves mastery. The goal is minimum time to useful feedback; mastery still requires recovery and transfer.

## Concept-action coverage

Build this before implementation:

```markdown
| Noun-action relationship | Project action | Observable evidence | Failure to inject | Mastery check |
|---|---|---|---|---|
| ... | ... | ... | ... | explain / predict / attack / delete / recover / transfer |
```

Merge project actions when one authentic action covers several relationships. Redesign the project when an essential relationship has no observable action or verifier.

## Decision record

Require the learner to record:

```markdown
## Framework choice
- Options considered:
- Criteria:
- Choice:
- Rejected option and reason:
- What evidence would change this choice:

## Strategy
- Checkpoint order:
- Why this order reduces uncertainty:

## Best practices and tools
- Must use:
- Deliberately skip:
- Tool choice and trade-off:
```

## Checkpoint pattern

Run each checkpoint as a map-updating loop:

```text
Reconstruct relevant relationship -> Predict -> Choose -> Execute
-> Observe -> Verify -> Explain -> Update the map
```

For every checkpoint, provide:

- one task;
- one constraint;
- one expected artifact;
- one verifier;
- one relationship the learner must explain or revise.

Do not reveal the full solution before the learner predicts and attempts. If blocked, give a progressively stronger hint, then a local example, then the solution only when needed.

## Acceptance criteria

Write criteria before implementation. Each criterion should specify:

```text
Given [starting condition]
When [action]
Then [observable result]
Verified by [independent test or evidence]
```

Include at least:

- one happy path;
- one invalid input or counterexample;
- one persistence or repeatability check;
- one recovery check;
- one boundary condition.

## Failure injection

Design failures across three surfaces:

- human: wrong assumption, skipped step, premature conclusion;
- AI/tool: fabricated result, invalid output, hidden default, partial completion;
- domain/system: corrupted state, missing resource, adversarial input, changed condition.

The learner must predict the failure, reproduce it safely, diagnose it, recover, and state what guard would prevent recurrence.

## Completion package

Preserve:

- the original goal and acceptance criteria;
- decision notes;
- commands or actions taken;
- outputs and failed attempts;
- independent verification results;
- the final concept-action coverage table;
- a short postmortem: which noun-action relationships changed in the learner's map and why.
