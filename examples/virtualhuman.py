"""The VirtualHuman lesson scenario from the AAMAS'05 paper.

The virtual teacher Valerie and the virtual student Sven attend a lesson.
Sven repeatedly disturbs the lesson; Valerie reproves him.  Later Valerie
encourages Sven, which over time makes him exuberant (section 5 of the
paper: "the encouragement from Valerie makes him slightly exuberant").

Configuration and character profiles are loaded from the YAML files
next to this script.
"""

from pathlib import Path

from alma_affect_kit import AffectEngine, load_character, load_config

HERE = Path(__file__).parent

engine = AffectEngine(load_config(str(HERE / "affect.yaml")))
engine.add_character(*load_character(str(HERE / "valerie.yaml")))
engine.add_character(*load_character(str(HERE / "sven.yaml")))


def show(affect_engine):
    """Print each character's current mood and dominant emotion."""
    for character in affect_engine:
        dominant = character.dominant_emotion
        label = f"{dominant.type} ({dominant.intensity:.2f})" if dominant \
            else "-"
        print(f"  {character.name:8s} mood={character.mood_word:22s} "
              f"dominant={label}")


print("Lesson starts:")
show(engine)

print("\nSven disturbs the lesson, Valerie reproves him (x8);"
      "\nsnapshot right after the last disturbance:")
for _ in range(8):
    engine.perceive_act("Disturb", performer="Sven", addressee="Valerie")
    engine.run(5.0)
    engine.perceive_act("Reprove", performer="Valerie", addressee="Sven")
    engine.run(20.0)
engine.perceive_act("Disturb", performer="Sven", addressee="Valerie")
engine.update(0.5)
show(engine)
engine.run(30.0)

print("\nValerie encourages Sven for a while (x25):")
for _ in range(25):
    engine.perceive_act("Encourage", performer="Valerie", addressee="Sven")
    engine.run(20.0)
show(engine)

print("\nA long quiet period; moods drift back to the defaults:")
engine.run(1500.0)
show(engine)
