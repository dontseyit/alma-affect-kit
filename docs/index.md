# alma-affect-kit v1.0.0

**alma-affect-kit** is a faithful Python implementation of ALMA, A Layered Model
of Affect (Patrick Gebhard, DFKI; AAMAS 2005), packaged as a reusable simulation engine
and toolkit for affect modelling. It models three interacting layers of affect, **emotions**, **moods** and **personality**, driven by world events and read back.

Simulation is deterministic and advances in time steps.

## Pages

| Page | What it covers |
|---|---|
| [Installation](installation.md) | Requirements, install options, file formats |
| [Usage](usage.md) | Quick start, characters, appraisals, rules, reading state |
| [The Model](the-model.md) | The theory: OCC emotions, PAD moods, Big Five personality, and how the three layers interact |
| [Appraisal](appraisal.md) | Emotion eliciting conditions, basic appraisal tags, the rule system, elicitation reference |
| [Simulation](simulation.md) | Time stepping, game-loop integration, dynamics timelines, determinism, performance |
| [Configuration](configuration.md) | Every parameter, the publication defaults, valid ranges and constraints, configuration file formats |
| [API Reference](api-reference.md) | The public API surface, module by module |
| [Examples](examples.md) | All the code in one place: quick start, rules, game-loop integration, file templates |
| [Fidelity Notes](fidelity.md) | What matches the papers exactly, and the documented choices where the papers are silent |

## At a glance

You create an engine and add characters. Each character has a Big Five
personality and can optionally have a rule configuration that describes how it
subjectively appraises.  For the rest of the session you do
two things: tell the engine what happens (events, acts, displays, or
direct appraisals) and advance simulated time.

Each appraisal produces emotions that decay over time.  While they last,
they pull the character's mood through PAD space, and when things quiet 
the mood drifts back to its default mood.  At any point you can
read a character's dominant emotion and its mood in plain words, such as
*slightly hostile* or *moderate exuberant*, and branch the character's
behaviour on them.

## Sources

* P. Gebhard. *ALMA, A Layered Model of Affect.* AAMAS 2005.
* P. Gebhard, M. Kipp, M. Klesen, T. Rist. *Adding the Emotional
  Dimension to Scripting Character Dialogues.* IVA 2003.
* P. Gebhard, M. Klesen, T. Rist. *Coloring Multi-Character Conversations
  through the Expression of Emotions.* ADS 2004.
* A. Ortony, G. L. Clore, A. Collins. *The Cognitive Structure of
  Emotions.* Cambridge University Press, 1988.
* A. Mehrabian. *Pleasure-arousal-dominance: A general framework for
  describing and measuring individual differences in temperament.*
  Current Psychology 14, 1996.
* A. Mehrabian. *Analysis of the Big-five Personality Factors in Terms of
  the PAD Temperament Model.* Australian Journal of Psychology 48(2), 1996.

Important: alma-affect-kit is an independent reimplementation based on the published papers
and is not affiliated with DFKI. ALMA is the original work of Patrick Gebhard (DFKI). 
While this implementation aims to faithfully reproduce the published model, it may 
contain deviations and cannot guarantee scientific accuracy. 
See [Fidelity Notes](fidelity.md) for further details.

---

*This documentation is an [MkDocs](https://www.mkdocs.org/) site.  To
preview it locally, run `pip install ".[docs]"` and then `mkdocs serve`;
`mkdocs build` produces a static site.  The markdown files in `docs/`
are the single source of truth.*
