# Versioning and Releases

## Version policy

alma-affect-kit follows [Semantic Versioning](https://semver.org/):
`MAJOR.MINOR.PATCH`.

Because the library is a reference implementation of a published model,
the compatibility promise covers **behaviour**, not just the API:

| Change | Bump |
|---|---|
| Bug fix that does not alter results for valid inputs; docs; packaging | PATCH |
| New API, new parameter with a default that preserves current behaviour | MINOR |
| Any change to a published constant (Table 2, regression coefficients, Fig. 3 defaults) or to an interpretive choice listed in the [Fidelity Notes](fidelity.md), i.e. anything that changes the numbers an existing simulation produces | MAJOR (MINOR while still 0.x) |
| Removing or renaming public API, configuration keys or profile-file keys | MAJOR (MINOR while still 0.x) |

While the version is `0.x`, minor releases may contain breaking changes;
they are always listed in the changelog under a *Model* or *Changed*
heading.  Users who need bit-for-bit reproducible simulations should pin
an exact version (`alma-affect-kit==0.1.0`).

## Where the version lives

The version string is defined **once**, in
`src/alma-affect-kit/_version.py`.  The package metadata reads it from there
(`dynamic = ["version"]` in `pyproject.toml`), and it is exported as
`alma-affect-kit.__version__`.  A git tag `vX.Y.Z` must match it; the
release workflow refuses to publish otherwise.

## Documentation versions

The documentation site is versioned with
[mike](https://github.com/jimporter/mike): every release publishes its
docs under `X.Y` (major.minor), the newest release is aliased `latest`
(the site's default), and the `main` branch is published continuously
as `dev`.  The version selector in the site header switches between
them, so readers of an older release see the docs, and the fidelity
notes, that match the code they installed.

## Release checklist

1. Move the *Unreleased* entries in `CHANGELOG.md` under a new
   `## [X.Y.Z] - YYYY-MM-DD` heading and update the comparison links.
2. Set `__version__ = "X.Y.Z"` in `src/alma-affect-kit/_version.py`.
3. Commit, then tag and push:

   ```bash
   git commit -am "Release X.Y.Z"
   git tag -a vX.Y.Z -m "alma-affect-kit X.Y.Z"
   git push && git push --tags
   ```

4. The `release` workflow verifies the tag matches `_version.py`, runs
   the tests, and builds the sdist and wheel.
5. The `docs` workflow publishes the versioned documentation and moves
   the `latest` alias.

A local dry run of the build is:

```bash
pip install build twine
python -m build && twine check dist/*
```
