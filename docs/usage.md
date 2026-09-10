# Usage

This page explains how you work with the engine, what the moving parts
are and how they fit together. Examples for everything described
here is collected on the [Examples](examples.md) page.

## The engine and its characters

An `AffectEngine` owns any number of characters and the global
computation parameters (an `AffectConfig` the defaults are the
publication values).

Each **character** is added by name, together with two things that
define who they are affectively:

* a **personality**, a Big Five profile (openness, conscientiousness,
  extraversion, agreeableness, neuroticism), each trait between -1 and
  +1.  The personality is fixed for the character's lifetime; the engine 
  derives the character's *default mood* from personality, this is also 
  the resting point the mood always drifts back.
* an optional **rule book**, the character's subjective appraisal
  rules, which decides how the character interprets events,
  acts and their perception. Characters still
  work without rules, and appraisals can be feed directly.

A character starts in its default mood with no active emotions.  You can
also hand it a different starting mood if the scene calls for one.

## Two ways to feed the simulation

**Direct appraisal:**  When the upstream logic already knows how something
should feel, you tell a character directly: *this was a moderately good
event*, *that was a bad act by someone else*.  These judgements
are expressed as emotion eliciting conditions, and constructors exist for 
all the standard cases (a good or bad event, a likely or unlikely future event 
and many others). The [Appraisal](appraisal.md) page explains the vocabulary and
exactly which emotion each judgement elicits.

**Perceived world input:**  In multi-character scenes it is usually
better to describe *what happened* once and let every character appraise
it through its own rules. The engine accepts four kinds of world input:

* a named **event** (e.g. "SunIsShining"), appraised by every character
  that has a basic rule for that name
* an **act** with a performer and optional target ("Sven attacks
  Valerie"), the performer appraises it with its *self* rules, the
  target with its *direct* rules, and everyone else with their
  *indirect* (listener) rules;
* an **emotion display**, a visible emotional cue such as shame, 
  appraised by the displaying character (*self*) and by
  observers (*other*);
* a **mood display**, a visible mood cue such as nervous idle
  behaviour, scoped the same way.

Because each character carries its own rules, one attack can leave the
victim distressed and angry, the attacker gloating, and a bystander
feeling pity, from a single call.

Both feeding styles return the emotions they elicited, so your downstream
logic can react immediately to what a character just felt.

## Advancing time

Nothing decays or drifts on its own, you advance simulated time
explicitly. Call the engine's `update()` method with the seconds that passed 
or let it step in the paper's 500 ms periods. Each update ages and expires 
active emotions, recomputes the emotion centre and moves every character's mood. 
See [Simulation](simulation.md) for the dynamics and game-loop patterns.

## Reading the affect back

At any moment a character exposes its full affective state:

| What | Meaning |
|---|---|
| Mood | A point in PAD space, plus its readable description, octant word and strength, e.g. *slightly hostile* |
| Default mood | The personality-derived resting mood, for comparison |
| Dominant emotion | The most intense active emotion above the behaviour threshold, or none, the one emotion that should visibly drive behaviour |
| Active emotions | Every currently decaying emotion, with intensity and cause |
| Emotion intensity | The current level of any one emotion type (its personality baseline when not active) |
| Affect output | A JSON-able snapshot of all of the above, for saves, telemetry or debugging |

The intended division of labour (from the paper's own system): 

The **dominant emotion** drives short-lived, pointed behaviour, facial
expressions, a spontaneous interjection, an emotional gesture.  The
**mood** drives everything slower, wording and phrasing, dialogue
strategy, idle behaviour, posture, how forcefully gestures are
performed.  The mood *word* ("moderate exuberant") is designed to be
switched on directly: eight octants and three strengths gives a standard 
vocabulary the further behaviours can branch over.

## Housekeeping

Characters can be reset (emotions dropped, mood back to default),
removed, or enumerated.  Profiles, personality, rules, can be
loaded from YAML (or JSON) files instead of being built in
code. See [Configuration](configuration.md).
