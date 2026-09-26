# Domain Research Template

Use this template when the user wants a research map, literature direction, professional comparison, or entry point into an unfamiliar field.

## Contents

- Define the research target
- Build the minimum noun-action system
- Ask the seven meta-word questions
- Build a compact evidence table
- Produce the research map

## 1. Define the research target

Capture:

```text
Question:
Decision or output this research should support:
Current knowledge:
Minimum useful outcome:
Available time:
Constraints:
Non-goals:
```

If the user gives a broad noun such as "investment", "AI", or "psychology", convert it into a concrete question before expanding the map.

## 2. Build the minimum noun-action system

Identify 5-10 essential nouns and the actions that make them useful:

```markdown
| Essential noun | Role in the system | Key verbs | Related nouns | Why it cannot be removed |
|---|---|---|---|---|
| ... | entity / state / artifact / role / concept | create / transform / compare / verify / ... | ... | ... |
```

Write relationships as executable statements:

```text
Noun A --verb--> Noun B
Actor --uses Tool to transform--> Input into Output
Verifier --checks--> Output against Evaluation criteria
Failure mode --breaks or distorts--> Relationship
```

For every relationship, explain:

- what starts the action;
- what changes;
- what observable result appears;
- what evidence would show the relationship is wrong.

Compress the system with a deletion question: if this noun, verb, or relationship disappears, can the learner still explain, operate, and verify the core loop? Remove it when the answer is yes.

## 3. Ask the seven meta-word questions

### Framework

- What are the field's major objects, relationships, boundaries, and schools of thought?
- Which frameworks explain the same problem differently?
- What would each framework cause us to notice or ignore?

### Evaluation criteria

- What makes an explanation, method, or result good in this field?
- Which criteria are measurable, and which require expert judgment?
- Who benefits from each criterion, and what trade-off does it hide?

### Strategy

- Given the user's goal and constraints, what routes are plausible?
- What sequence reduces uncertainty fastest?
- What evidence would cause the route to change?

### Best practices

- Which practices are widely used, and under what conditions?
- Which are conventions rather than evidence-backed requirements?
- What common advice is inappropriate for this user's scale or goal?

### Available tools

- Which tools support discovery, execution, measurement, simulation, or verification?
- What prerequisite, cost, lock-in, or data risk comes with each tool?

### Failure modes

Separate:

- learner/researcher failures: confirmation bias, vague questions, premature convergence, copying without understanding;
- AI/tool failures: fabricated sources, correlated model errors, hidden defaults, stale information, benchmark overfitting;
- domain failures: conditions under which the method itself breaks.

### Evidence and verifier

- What primary source, official documentation, dataset, experiment, test, or real-world outcome can decide the claim?
- Is the verifier independent of the person or model that produced the answer?
- What remains unresolved after verification?

## 4. Build a compact evidence table

```markdown
| Claim | Evidence type | Source or test | Status | What could overturn it? |
|---|---|---|---|---|
| ... | primary / secondary / experiment | ... | verified / provisional / open | ... |
```

Do not use citation count, model confidence, or multi-model agreement as a substitute for checking the source.

## 5. Produce the research map

Return:

1. one concrete research question;
2. a table of 5-10 essential nouns, their key verbs, and why each is necessary;
3. a compact relationship map showing how actions connect the nouns;
4. at most three frameworks or strategies;
5. one recommended route and its criteria;
6. known failure modes and counterarguments;
7. verified evidence, provisional material, and open questions;
8. the shortest next action that produces useful feedback;
9. the practice action and mastery check connected to each essential relationship.

For a substantial research task, update the map after each evidence round rather than treating the first outline as final.
