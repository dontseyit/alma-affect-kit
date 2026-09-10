# Changelog

All notable changes to this project are documented here.  The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project adheres to [Semantic Versioning](https://semver.org/).

Because this library is a reference implementation of a published
model, **any change to a published constant, a publication default or
the mood/emotion dynamics is treated as a breaking change** and is
called out under a *Model* heading, even when the API is unchanged.

## [Unreleased]

## [0.1.0] - 2026-08-25

Initial release.

### Added

- The three-layer ALMA model (Gebhard, AAMAS'05): OCC emotions (24
  types, Table 2 PAD mapping, linear/exponential/tanh decay), PAD moods
  with the pull/push mood change function and mood return, Big Five
  personality with Mehrabian's default-mood regression and per-emotion
  baselines.
- Appraisal: emotion eliciting conditions, the OCC elicitation rules
  including compound emotions, basic appraisal tags (IVA'03), and
  per-character subjective rule books (basic events, acts scoped
  self/direct/indirect, emotion and mood displays).
- Multi-character `AffectEngine` with deterministic time stepping,
  world-input dispatch and JSON-able affect snapshots.
- YAML (default) and JSON loading of configurations and character
  profiles, with strict validation; one-to-one mapping from the paper's
  AffectML documents.
- Publication defaults for every parameter, all configurable; the
  `mood_change_distance` parameter making the paper's ambiguous
  octant-centre calibration explicit.
- Documentation site (MkDocs) with a fidelity ledger of every verbatim
  value and every interpretive choice.

[Unreleased]: https://github.com/OWNER/alma-affect-kit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/alma-affect-kit/releases/tag/v0.1.0
