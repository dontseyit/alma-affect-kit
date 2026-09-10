# The Model

ALMA (*A Layered Model of Affect*, Gebhard, AAMAS 2005) simulates three
interacting kinds of affect as they occur in human beings, distinguished
by how long they last and what they influence:

| Layer | Duration | Theory | Bound to | Role |
|---|---|---|---|---|
| **Emotions** | short-term (seconds) | OCC (Ortony, Clore & Collins 1988) | a specific event, action or object | colour immediate reactions: facial expressions, gestures, wording |
| **Moods** | medium-term (minutes) | Mehrabian's PAD temperament space | nothing concrete, a longer-lasting stable affective state | steer strategies: dialogue style, idle behaviour, posture |
| **Personality** | long-term (permanent) | Big Five / Five Factor Model (McCrae & John 1992) | the individual | frames everything: the default mood and emotional dispositions |

## How the layers interact

```
world input ──► appraisal rules ──► EECs ──► OCC rules ──► active emotions
                                                                │ decay
             personality ──► emotion baselines ─────────────────┤
                                                                ▼
             personality ──► default mood          virtual emotion centre
                                  │                             │
                                  ▼           pull / push       ▼
                            mood return  ◄──────────────────► mood
```

1. World input (events, acts, displays) is **appraised** through each
   character's subjective rules into *emotion eliciting conditions* (EECs).
2. The OCC rules turn EECs into **active emotions** with intensities,
   biased by personality baselines. Active emotions **decay** back to
   their baseline within the emotion decay time (default 20s).
3. All currently active emotions form a **virtual emotion centre** in
   PAD space, which drags the mood around via the **pull/push mood
   change function**.
4. Absent active emotions, the mood slowly **returns** to the
   personality-derived **default mood**.

## Layer 1: Emotions (OCC)

ALMA's "EmotionEngine" implements the OCC cognitive model of emotions. 
Here emotions are valenced reactions to events that concern the character, 
to actions of agents the character holds responsible, and to objects. 
Appraising these produces EEC variables. Their signs select among the 24 emotion types, 
and their absolute values determine intensity. 
See Appraisal for the full reference.

Each emotion type maps to a point in PAD space (paper, Table 2):

| Emotion | P | A | D | Octant |
|---|---|---|---|---|
| Admiration | 0.5 | 0.3 | -0.2 | +P+A-D Dependent |
| Anger | -0.51 | 0.59 | 0.25 | -P+A+D Hostile |
| Disliking | -0.4 | 0.2 | 0.1 | -P+A+D Hostile |
| Disappointment | -0.3 | 0.1 | -0.4 | -P+A-D Anxious |
| Distress | -0.4 | -0.2 | -0.5 | -P-A-D Bored |
| Fear | -0.64 | 0.60 | -0.43 | -P+A-D Anxious |
| FearsConfirmed | -0.5 | -0.3 | -0.7 | -P-A-D Bored |
| Gloating | 0.3 | -0.3 | -0.1 | +P-A-D Docile |
| Gratification | 0.6 | 0.5 | 0.4 | +P+A+D Exuberant |
| Gratitude | 0.4 | 0.2 | -0.3 | +P+A-D Dependent |
| HappyFor | 0.4 | 0.2 | 0.2 | +P+A+D Exuberant |
| Hate | -0.6 | 0.6 | 0.3 | -P+A+D Hostile |
| Hope | 0.2 | 0.2 | -0.1 | +P+A-D Dependent |
| Joy | 0.4 | 0.2 | 0.1 | +P+A+D Exuberant |
| Liking | 0.40 | 0.16 | -0.24 | +P+A-D Dependent |
| Love | 0.3 | 0.1 | 0.2 | +P+A+D Exuberant |
| Pity | -0.4 | -0.2 | -0.5 | -P-A-D Bored |
| Pride | 0.4 | 0.3 | 0.3 | +P+A+D Exuberant |
| Relief | 0.2 | -0.3 | 0.4 | +P-A+D Relaxed |
| Remorse | -0.3 | 0.1 | -0.6 | -P+A-D Anxious |
| Reproach | -0.3 | -0.1 | 0.4 | -P-A+D Disdainful |
| Resentment | -0.2 | -0.3 | -0.2 | -P-A-D Bored |
| Satisfaction | 0.3 | -0.2 | 0.4 | +P-A+D Relaxed |
| Shame | -0.3 | 0.1 | -0.6 | -P+A-D Anxious |

### Decay

An elicited emotion decays from its initial intensity back to its personality baseline 
within the emotion decay time (20s by default). The decay curve is linear by default and 
can also be exponential, hyperbolicus, or a sigmoid that starts slowly, speeds up in the 
middle and levels off at the end.

### Dominant emotion

Emotions should not a priori influence behaviour measurably: only the
**most intense active emotion whose intensity exceeds a threshold**
(default 0.4) is reported as `dominant_emotion` for behaviour control.
All active emotions, dominant or not, still drive the mood.

## Layer 2: Moods (PAD space)

Mood is a point in Mehrabian's three-dimensional
**pleasure–arousal–dominance** space, each axis in [-1, 1]. The eight
octants carry discrete mood names (paper, Table 1):

|  |  |
|---|---|
| **+P+A+D** Exuberant | **-P-A-D** Bored |
| **+P+A-D** Dependent | **-P-A+D** Disdainful |
| **+P-A+D** Relaxed | **-P+A-D** Anxious |
| **+P-A-D** Docile | **-P+A+D** Hostile |

**Mood strength** is the Euclidean norm of the PAD vector.  The longest
distance inside an octant, √3, is divided into three equal parts:
**slightly** [0, √3⁄3), **moderate** [√3⁄3, 2√3⁄3), **fully**
[2√3⁄3, √3]. A mood of (0.25, −0.18, 0.12) reads *slightly relaxed*.

### The virtual emotion centre

Every active emotion is a point in PAD space (via the table above).
Their average position is the **virtual emotion centre** (VEC); its
intensity is the average of the active emotions' intensities (max 1.0).
The VEC jumps around erratically as emotions come and go, so it is not
the mood itself, but the *force* that changes the mood smoothly.

### The pull and push mood change

* **Pull phase**, while the current mood lies between the PAD origin
  and the VEC, the mood is *attracted towards* the VEC.
* **Push phase**, once the mood is beyond (or at) the VEC, it is
  *pushed further* into its current octant. A person's mood intensifies 
  as they undergo experiences that reinforce it. Repeated similar 
  emotions therefore escalate a mood from *slightly* to *moderate* to *fully*.

The intensity of the VEC determines the speed. At the maximum intensity 
setting, the mood travels the distance between the centers of two adjacent 
octants (1.0 PAD unit) within the **mood transition time** (which is 10 minutes 
by default)

### Mood return

The mood tends to drift back to the **default mood**. The longest octant distance (√3) 
is travelled in the **mood return time**, 20 minutes by default. The return applies while 
no active emotions exist (can be changed by `mood_return_mode="idle|always"`).

## Layer 3: Personality (Big Five)

A character's personality is a Big Five profile, **openness,
conscientiousness, extraversion, agreeableness, neuroticism**, each
trait in [-1, 1]. It influences the model in two ways.

### Default mood

Mehrabian's regression of the Big Five onto PAD defines the character's
resting mood:

```
Pleasure  =  0.21·Extraversion + 0.59·Agreeableness + 0.19·Neuroticism
Arousal   =  0.15·Openness + 0.30·Agreeableness − 0.57·Neuroticism
Dominance =  0.25·Openness + 0.17·Conscientiousness
             + 0.60·Extraversion − 0.32·Agreeableness
```

The paper's worked example: openness 0.4, conscientiousness 0.8,
extraversion 0.6, agreeableness 0.3, neuroticism 0.4 → default mood
(P 0.38, A −0.08, D 0.50), octant *Relaxed*.

### Emotion baselines

Personality biases emotion intensities with a **baseline intensity** per
emotion type, "an extravert character's baseline intensity for joy is
0.15, whereas an introvert character's would be 0.0" (IVA'03).  Elicited
intensities are raised by the baseline, and emotions decay back *to* the
baseline rather than to zero. The default weight table (positive
emotions from extraversion + agreeableness, negative from neuroticism,
small conscientiousness/openness terms for the attribution/attraction
groups) is a documented interpolation from the papers' qualitative
guidance, see [Fidelity Notes](fidelity.md).
