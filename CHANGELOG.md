# Changelog

All notable changes to this project are documented in this file. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-05-23

Initial release. Five composable Python modules for distributed-systems
constraint math (Eisenstein lattice quantization, deadband funnels, Laman
rigidity, metronome consensus, holonomy verification), plus a companion
Rust crate (`rust/`, `constraint-theory-world-music`) applying the same
mathematical primitives to music theory (scales, tuning systems, rhythm).

### Added

- `constraint_theory_core.lattice` — Eisenstein A₂ lattice quantization,
  every point within ρ = 1/√3 of a lattice point by construction.
- `constraint_theory_core.temporal` — narrowing deadband funnel
  (ε(t) = ε₀ · e^(−λt)) so drift converges to zero or triggers an anomaly.
- `constraint_theory_core.rigidity` — Laman-rigidity checks for
  communication graphs (exactly 2n−3 edges, every edge load-bearing).
- `constraint_theory_core.metronome` — distributed consensus across
  Laman-connected agents with optimal coupling α* = 2/(λ₂ + λₙ).
- `constraint_theory_core.holonomy` — cycle-consistency verification in
  tiled constraint systems, O(log N) fault isolation via binary bisection.
- `constraint_theory_core.exercises` — exercise generator for classroom
  use.
- `constraint_theory_core.genre_brain` — a fifth module exploring the
  same constraint math applied to musical genre/style classification.
- Property-based tests (Hypothesis), edge-case tests, and benchmark
  suite (pytest-benchmark) alongside the core unit tests — 308 tests
  total, verified passing on extraction.
- `rust/` — a separate Cargo crate, `constraint-theory-world-music`:
  world music scales, tuning systems, ornaments, rhythms, and a "Penrose
  music" module (`living.rs`: `MusicalCell`, `JazzSession`,
  `TradingFours`, `CallAndResponse`, `Vamp`).
- `soft_snap` ε-parameterization across all constraint modules.

### Fixed

- Division-by-zero in `algebraic_connectivity`/`optimal_coupling` for
  graphs with fewer than 2 nodes.
- Input validation guards found by stress testing.
- `pyproject.toml` build backend and license classifier.

## [Unreleased]

### Changed

- Extracted from a stray `master` branch on
  `purplepincher/constraint-theory-core` (a different, unrelated Rust
  crate) into this dedicated repo, full history preserved. Renamed the
  distribution to `constraint-theory-distributed` to avoid confusion
  with that repo (the Python import name, `constraint_theory_core`,
  is unchanged).
