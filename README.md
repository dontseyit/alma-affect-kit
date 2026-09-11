# ALMA Affect Kit

A faithful, standalone Python implementation of **ALMA** (Patrick Gebhard,
DFKI, *ALMA: A Layered Model of Affect*, AAMAS 2005) as a reusable
simulation engine.

This library was developed as part of my character development work for robotics projects;
it was used to experiment with characters having emotions and personalities with mood dynamics.
It transfers the model into a Python module and allows execution of the deterministic,
time-step driven simulation described in the original publication.

**Important**: This is an independent reimplementation; it is not affiliated with DFKI. 
ALMA is the original work of Patrick Gebhard (DFKI). While this implementation aims to faithfully 
reproduce the published model, it may contain deviations and cannot be guaranteed to be 
scientifically accurate. See [Fidelity Notes](docs/fidelity.md) for further details.


## Documentation

MkDocs site built from `docs/*`. See [docs/](docs/index.md) for individual files.

All available at https://dontseyit.github.io/alma-affect-kit.


## Install

**Requirements:** Python ≥ 3.9

```bash
pip install .        # install with the PyYAML dependency
```

For development:
```bash
pip install -e ".[docs]" pytest
```

## Quick start

```python
from alma_affect_kit import AffectEngine, Personality, good_event

engine = AffectEngine()

valerie = engine.add_character("Valerie", Personality(
    openness=0.4, conscientiousness=0.8, extraversion=0.6,
    agreeableness=0.3, neuroticism=0.4))
print(valerie.mood_word)   # 'moderate relaxed'

engine.appraise("Valerie", good_event(0.7, cause="sun is shining"))
engine.update(0.5)
print(valerie.dominant_emotion)  # ActiveEmotion(Joy, intensity=0.80, ...)
```

Call `engine.update(dt)` in loop, or `engine.step()` / `engine.run(seconds)`
to advance in fixed steps. The simulation is deterministic, so the same inputs
always produce the same outputs.

## Configuration

Configurations and character profiles support YAML or JSON files, 
the paper's AffectML documents replaced with a modern format (see the
[Configuration docs](docs/configuration.md) for the AffectML to YAML
mapping).

The structure mirrors the library's dataclasses (times in **seconds**);
see [examples/affect.yaml](examples/affect.yaml) and
[examples/valerie.yaml](examples/valerie.yaml) for complete examples.

## Development

```bash
pytest                      # test suite
mkdocs serve               # docs site at http://127.0.0.1:8000
mkdocs build --strict      # validate and build docs
```

## References

* P. Gebhard. *ALMA, A Layered Model of Affect.* AAMAS 2005.
* P. Gebhard, M. Kipp, M. Klesen, T. Rist. *Adding the Emotional Dimension
  to Scripting Character Dialogues.* IVA 2003.
* P. Gebhard, M. Klesen, T. Rist. *Coloring Multi-Character Conversations
  through the Expression of Emotions.* ADS 2004.
* A. Ortony, G. L. Clore, A. Collins. *The Cognitive Structure of
  Emotions.* Cambridge University Press, 1988.
* A. Mehrabian. *Pleasure-arousal-dominance: A general framework for
  describing and measuring individual differences in temperament.* Current
  Psychology 14, 1996.
* A. Mehrabian. *Analysis of the Big-five Personality Factors in Terms of
  the PAD Temperament Model.* Australian Journal of Psychology 48(2), 1996.

---

**AI Disclaimer** 

In this project, AI was used to extract information, generate code, and documentation under human guidance
and oversight. It was used in various personal projects and subsequently shared with the open-source community.
All documents and most code were human-reviewed and updated after the initial AI generation, but
there may still be overlooked or sloppy parts.
