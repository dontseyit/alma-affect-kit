# alma-affect-kit v1.0.0

**alma-affect-kit** is a faithful Python implementation of ALMA, A Layered Model of Affect 
(Patrick Gebhard, DFKI; AAMAS 2005), packaged as a reusable simulation engine and toolkit for affect modelling. 
It models three interacting layers of affect, **emotions**, **moods** and **personality**, driven by world events.

You create an engine and populate it with characters. Each character has a Big Five personality profile and may also
include a set of appraisal rules that define how it interprets events from its own perspective. During a session, you
provide the engine with occurrences such as events, actions, displays, or direct appraisals, and advance the simulation
over time.

Each appraisal can trigger emotions that fade as time passes. While they remain active, these emotions shape the
character's mood within PAD space. Once the situation settles, the mood gradually returns toward its baseline state. A
character's dominant emotion and mood can then be expressed in everyday terms, such as "slightly hostile" or
"moderately exuberant," making it possible to condition behaviour on those affective states.

## Pages

| Page | |
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

**Important:** alma-affect-kit is an independent reimplementation based on the published papers
and is not affiliated with DFKI. ALMA is the original work of Patrick Gebhard (DFKI). 
While this implementation aims to faithfully reproduce the published model, it may 
contain deviations and cannot guarantee scientific accuracy. 
See [Fidelity Notes](fidelity.md) for further details.

---

**AI Disclaimer** 

In this project, AI was used to extract information, generate code, and documentation under human guidance
and oversight. It was used in various personal projects and subsequently shared with the open-source community.
All documents and most code were human-reviewed and updated after the initial AI generation, but
there may still be overlooked or sloppy parts.
