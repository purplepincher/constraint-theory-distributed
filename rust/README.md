# constraint-theory-world-music

World music scales, tuning systems, ornaments, rhythms, cohomology, and Penrose music — the constraint-math primitives from the [Python `constraint_theory_core` package](../) applied to musical structure instead of distributed systems. 85 passing tests. Zero runtime dependencies.

> Companion crate to [constraint-theory-distributed](../), extracted together with it from a stray branch on `purplepincher/constraint-theory-core`. Not yet published to crates.io.

## What it does

Seven modules, each a self-contained piece of music theory:

| Module | What | Scale |
|--------|------|-------|
| `scales` | World music scales across 6 cultures | 36 scales |
| `tuning` | Tuning systems (equal temperament, just intonation, shruti, quarter-tone, pentatonic, meantone, pythagorean) | 7 systems |
| `ornaments` | Ornamentation curves (meend, gamak, quarter bends, grace notes, murki, shakes) | 6 types |
| `rhythms` | World rhythm patterns (clave, bell, tala, iqa, swing) | 26 patterns |
| `cohomology` | Musical cohomology — detects emergent structure in chord transition graphs | — |
| `penrose` | Aperiodic rhythm/melody generation via 5D → 2D cut-and-project | — |
| `living` | Biological metaphor for ensemble improvisation — cells with genomes express musical output through shared context; a `JazzSession` orchestrates them through Head → Solo → Trading → Collective → Coda | — |

## Installation

Not yet published to crates.io. Add as a path or git dependency:

```toml
[dependencies]
constraint-theory-world-music = { git = "https://github.com/purplepincher/constraint-theory-distributed", subdir = "rust" }
```

(Cargo does not support `subdir` natively — vendor the `rust/` directory or clone the repo and use a `path` dependency instead.)

## Quick start

```rust
use constraint_theory_world_music::tuning::ratio_to_cents;

// Convert a frequency ratio to cents
let cents = ratio_to_cents(1.5); // perfect fifth
println!("{cents:.2} cents"); // ~701.96
```

## Testing

```bash
cd rust
cargo test               # 85 tests
cargo fmt --check
cargo clippy -- -D warnings
```

## License

MIT
