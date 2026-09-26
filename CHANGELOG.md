# Changelog

All notable changes to this project. Versions follow [semver](https://semver.org/); both editions share one version number.

## [1.0.0] — 2026-09-26

First public release.

- Two installable editions: `hig42-design` (English) and `hig42-design-zh-tw` (Traditional Chinese), published through the `okle42` Claude Code plugin marketplace.
- Nine reference files: typography & layout, color & materials, Liquid Glass (iOS/macOS 26 → 27), macOS components, charts & live data, notifications & background apps, accessibility, Apple-style web, Traditional Chinese UI writing.
- `assets/apple-web-base.css`: system colors, light / dark / increased contrast, grouped lists, switches, segmented controls.
- Every Swift sample type-checks against the Xcode 27 SDK; two independent cross-check rounds (68 + 27 claims sampled, 18 errors fixed before release); 145 sources in `SOURCES.md`.
- Repository tooling: `tools/check.py`, `tools/package.py`, CI workflow, issue templates, reproducible A/B test in `evals/`.
