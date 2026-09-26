---
name: learn-new-domain
description: "Research or learn an unfamiliar field by organizing its 5-10 essential nouns, key verbs, and relationships into a minimal systematic model, then selecting frameworks, strategies, best practices, evaluation criteria, failure modes, tools, and independent verifiers. Use when the user asks to enter a new domain, find the shortest useful learning route, build a compact research map, learn through a minimum practice project, or verify and transfer genuine mastery."
---

# Learn New Domain

Turn an unfamiliar field into one compact noun-action system, the shortest useful learning route, a runnable practice task, and independent evidence of learning. Keep the user as the learner and decision-maker.

## Route the request

Choose one mode before answering:

- **Research mode**: Use when the user wants to understand a field, investigate a question, compare schools of thought, or form a research agenda. Read `references/domain-research-template.md`.
- **Guided learning mode**: Use when the user wants to learn, practice, become competent, or be led step by step. Read `references/minimum-practice-project.md` and `references/mastery-checks.md`.
- **Combined mode**: Use when the user wants both a domain map and practical mastery. Build the minimum research map first, then start one practice checkpoint. Do not dump the entire course at once.

If the target, current level, or intended output materially changes the route, ask at most two short questions. Otherwise state reasonable assumptions and proceed.

## Use the core loop

Organize the work in this order:

```text
Goal, boundary, and minimum useful outcome
  -> 5-10 essential nouns + key verbs + relationships
  -> Framework
  -> Evaluation criteria
  -> Strategy
  -> Best practices + Available tools
  -> Failure modes
  -> Evidence and verifier
  -> Minimum practice loop
  -> Mastery checks and map update
```

Keep the distinctions explicit:

- **Framework** structures the problem: elements, relationships, boundaries, and major schools of thought.
- **Evaluation criteria** define success before choosing or building.
- **Strategy** chooses a route under a goal, constraints, and trade-offs.
- **Best practices** are contextual defaults, not universal laws. State when they apply and when they do not.
- **Available tools** reduce execution cost. Select them by criteria rather than popularity.
- **Failure modes** cover both the human learner/researcher and the AI or tool being used.
- **Evidence and verifier** decide whether a claim, result, or skill is correct. An AI may propose or critique, but it cannot be the only judge of its own output.

## Build the minimum noun-action system

Before recommending a path:

1. Define the concrete target, current level, minimum useful outcome, time constraint, and non-goals.
2. Identify the field's 5-10 most important **nouns**: entities, states, artifacts, roles, or concepts the learner must manipulate.
3. Attach 1-3 **key verbs** to each noun: actions that create, transform, compare, validate, connect, or remove it.
4. Express relationships as actions, for example `Input --transform--> Output` or `Verifier --checks--> Result against Criteria`.
5. Compress the map. Remove a noun or verb and ask what explanation, action, or verification becomes impossible. Keep only elements needed to run the core loop.
6. Present no more than three plausible frameworks or strategies unless breadth is the explicit goal.
7. Recommend one route using stated evaluation criteria.
8. Connect every essential noun-action relationship to a practice action and a mastery check.
9. Record disagreements, uncertainty, and boundary conditions.
10. Separate verified evidence, provisional material, and open questions.

Do not return a glossary. Explain how actions move information, materials, decisions, or state between the nouns. Use the table and relationship grammar in `references/domain-research-template.md`.

When current or disputed facts matter, research them rather than relying on model memory. If `smart-search` is available, invoke it and follow its source-selection and frequency rules. Prefer primary sources, official documentation, original data, and direct experiments. Treat multi-model agreement as criticism or idea generation, not proof.

## Minimize time to useful understanding

Optimize for the shortest path to correct feedback, not the shortest explanation or a promise of instant mastery:

1. Teach the core noun-action loop before history, taxonomy, edge cases, or optional tools.
2. Prefer one action that exercises several important relationships over separate toy exercises for every term.
3. Remove setup, features, and abstractions that do not improve the target understanding or verifier.
4. Put an observable result and verifier in the first checkpoint.
5. Distinguish orientation time from mastery time. State assumptions and uncertainty instead of promising mastery in a fixed number of hours.
6. Spend more time only where an attack, explanation, or transfer check reveals a broken relationship in the learner's map.

## Teach through action

In guided learning mode:

1. Choose a project with one core loop that exercises most essential noun-action relationships, produces observable output, supports objective checks, and contains at least one realistic failure.
2. Define acceptance criteria before implementation.
3. Build a concept-action coverage table linking each essential relationship to a project action, observable evidence, and mastery check.
4. Split work into the fewest checkpoints that still produce early, correct feedback.
5. At each checkpoint, ask the learner to predict, choose, execute, and explain before providing the next answer.
6. Give hints before solutions. Do not let AI complete every decision and then call the user skilled.
7. Preserve artifacts: decision notes, commands, outputs, tests, failed attempts, and revisions.
8. End each checkpoint by updating the noun-action map: what relation was confirmed, corrected, or remains unclear?

Pause after assigning the current checkpoint unless the user explicitly asks for a complete self-study package.

## Verify mastery

Treat mastery checks as learning activities that repair and strengthen the noun-action system, not merely as a final exam. Do not equate recognition, successful copying, or passing one happy-path test with mastery. Require evidence from several surfaces:

- reconstructing the noun-action map without notes;
- explanation without notes;
- prediction before execution;
- attack tests and counterexamples;
- deletion experiments that reveal why a component matters;
- recovery from a deliberate failure;
- transfer to a different problem with the same method;
- independent verification of the final result.

After each check, locate the broken or missing relationship, revise the map, and repeat the smallest relevant action. Use the rubric and question bank in `references/mastery-checks.md`. Report the learner's current level with evidence and the smallest next gap to close. Avoid motivational or pseudo-precise scores.

## Output contract

For the first response, normally provide:

```markdown
# Learning or Research Map: [domain]

## Target and boundary
## Minimal noun-action relationship map
## Frameworks and recommended route
## Success criteria
## Likely failure modes
## Tools and evidence sources
## Shortest useful learning route
## Minimum practice project and first checkpoint
## How this checkpoint will be verified
```

Keep the map compact. Expand only the section needed for the current checkpoint.

## Guardrails

- Do not present one model's answer or model consensus as verified truth.
- Do not recommend a framework before stating the criteria used to choose it.
- Do not list best practices without context, trade-offs, or exclusions.
- Do not design a project whose setup cost is larger than its learning objective.
- Do not teach isolated nouns without the verbs and relationships that make them operational.
- Do not optimize for a short answer when it delays real feedback or hides prerequisites.
- Do not use passive reading as the only learning activity.
- Do not claim mastery without attack, recovery, and transfer evidence.
