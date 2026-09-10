# Simulation

The engine is **deterministic and time-step driven**: nothing happens
between calls, and the same inputs at the same times always produce the
same affective trajectories.  There is no internal clock, no threads and
no randomness, you decide how fast simulated time passes.

## Advancing time

There are three ways to move the simulation forward, all equivalent:

* **update(dt)**, advance every character by `dt` seconds; the natural
  call from a game loop, with your frame or tick delta.
* **step(n)**, advance in whole update periods (500 ms by default, the
  paper's rate).
* **run(seconds)**, simulate a stretch of time in period-sized slices;
  convenient in tests and offline simulation.

One update does three things per character, in order: age all active
emotions and drop the fully decayed ones; recompute the virtual emotion
centre from what remains; move the mood one step (pulled/pushed by the
emotion centre, or drifting back to the default mood when no emotions
are active).  The engine also keeps a running total of simulated time.

Any step size works, the dynamics are calibrated in seconds, not in
ticks, but very large steps make the mood's path coarser: a single
ten-minute update moves the mood in one straight line, while the same
ten minutes in half-second steps bends smoothly around a moving emotion
centre.  Frame-rate steps at 60 fps are perfectly fine and cheap.

## Fitting it into a game loop

Treat the affect engine like any other simulation system: give it time
every tick, give it events when they happen, read it when you render or
decide behaviour.

* **Time**: call update with the frame delta each tick, or accumulate
  the delta and update in fixed 500 ms slices if you prefer a fixed
  affect rate alongside a variable frame rate.
* **Events**: wherever your game already dispatches gameplay events
  (an insult, a victory, a threat appearing), add a call that lets the
  affected characters perceive it, either as a named event/act through
  their rules, or as a direct appraisal.
* **Output**: when choosing an animation, a line of dialogue or an idle
  behaviour, read the character's mood word and dominant emotion at
  that moment.

To run affect faster or slower than real time, scale the `dt` you pass,
because the model is calibrated in seconds, scaling time is exactly
equivalent to scaling all three time constants together.

A worked game-loop pattern is on the [Examples](examples.md) page.

## What a typical timeline looks like

With publication defaults, a single strong negative appraisal (a very
undesirable event, desirability −0.8) plays out like this:

| Time | Emotions | Mood |
|---|---|---|
| 0 s | Distress elicited at about 0.8 | starts drifting towards the Distress point in PAD space |
| 10 s | decayed to about 0.4 (linear decay) | still drifting, more slowly, the emotion centre's intensity fell with it |
| 20 s | fully decayed; the active set is empty | begins the slow return to the default mood |
| approx 20 min later |  | back at the default mood |

Two things follow from the calibration, and they are the heart of the
model's feel:

* **A single emotion barely dents the mood.**  Twenty seconds of pull
  at intensity 0.8 moves the mood only about 0.03 PAD units.  Moods are
  medium-term by construction, one insult does not ruin an afternoon.
* **A stream of similar emotions escalates the mood.**  Repeated
  appraisals keep the emotion centre alive; once the mood crosses the
  centre, the *push phase* drives it deeper into its octant.  That is
  how repeated fear experiences take a character from *slightly
  anxious* through *moderate* to *fully anxious*, and why a character
  who has been mistreated for ten minutes stays hostile for a while
  even after the mistreatment stops.

## Multi-character scenes

Every character appraises the same world input through its own rules,
so a single perceived act fans out into different emotions per observer
, the attacker, the victim and each bystander all react in character.
Perception calls accept an optional list of characters, which is how
you scope an input to, say, only the characters in the same room.

## Determinism, saving and restoring

* There is no randomness anywhere.  The same calls in the same order
  with the same time steps reproduce identical states, replays and
  tests are exact.
* A character's complete dynamic state is small: its mood point plus
  its active emotions (type, intensity values, age, cause).  The
  affect-output snapshot is JSON-able and suits save games and
  telemetry; restoring exactly means recreating the characters and
  re-adding their active emotions with their ages.
* Resetting a character drops its emotions and returns its mood to the
  default mood.

## Constraints and guarantees

* Update requires a non-negative time step; negative values are
  rejected.
* The mood always stays inside the PAD cube (−1 to +1 on every axis).
* Emotion intensities stay in [0, 1] and never fall below the
  character's personality baseline; an elicitation weaker than the
  baseline is raised to it and stays active for the decay time.
* The engine is **not thread-safe**: drive one engine from one thread,
  or guard it with your own lock.  Separate engines are fully
  independent.
* A character's personality, baselines and default mood are fixed when
  the character is added; changing the shared configuration afterwards
  affects newly elicited emotions and the ongoing mood dynamics, but
  does not recompute those per-character constants.

## Performance

Cost per update is proportional to characters × active emotions, with
small constants, a handful of float operations per emotion and one
square root per mood step.  Emotion intensities are memoized per age and
personality baselines are precomputed per character.  Hundreds of
characters at the 500 ms period is trivial; per-frame updates at 60 fps
are fine too.  Appraisal cost is proportional to the number of matching
rules per perceived input.
