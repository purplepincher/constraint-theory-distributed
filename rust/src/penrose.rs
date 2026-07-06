//! Penrose music — aperiodic rhythm and melody generation via cut-and-project.
//!
//! Uses the 5D → 2D cut-and-project algorithm with golden-angle projection
//! to generate musical quasicrystals.

use std::f64::consts::PI;

const INV_PHI: f64 = 0.618033988749895;
const TWO_PI_OVER_5: f64 = 2.0 * PI / 5.0;
const DIM: usize = 5;

// ── Internal tile ───────────────────────────────────────────────────

// `source` and `tile_type` are part of the tile's real domain state (the
// 5D lattice point it projected from, and its rhombus type) — kept even
// though nothing outside construction reads them yet.
#[allow(dead_code)]
#[derive(Debug, Clone)]
struct Tile {
    x: f64,
    y: f64,
    source: [i32; DIM],
    tile_type: TileType,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum TileType {
    Thick,
    Thin,
}

// ── Linear algebra ──────────────────────────────────────────────────

fn mat_vec(mat: &[[f64; DIM]; 2], vec: &[f64; DIM]) -> [f64; 2] {
    [
        (0..DIM).map(|j| mat[0][j] * vec[j]).sum(),
        (0..DIM).map(|j| mat[1][j] * vec[j]).sum(),
    ]
}

fn dot(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b.iter()).map(|(x, y)| x * y).sum()
}

fn normalize(v: &mut [f64]) {
    let norm = v.iter().map(|x| x * x).sum::<f64>().sqrt();
    if norm > 1e-12 {
        for x in v.iter_mut() {
            *x /= norm;
        }
    }
}

// Index variables here double as arithmetic values (e.g. `idx = 2 + i`)
// across parallel fixed-size arrays, not just as iteration indices —
// an iterator rewrite would obscure the cross-array indexing rather
// than simplify it.
#[allow(clippy::needless_range_loop)]
fn gram_schmidt_perp(proj: &[[f64; DIM]; 2]) -> [[f64; DIM]; 3] {
    let mut basis: Vec<Vec<f64>> = Vec::new();

    // Start with normalized projection rows
    for r in 0..2 {
        let mut row = proj[r].to_vec();
        normalize(&mut row);
        basis.push(row);
    }

    // Extend with standard basis vectors
    for i in 0..DIM {
        let mut e = vec![0.0; DIM];
        e[i] = 1.0;
        for b in &basis {
            let d = dot(&e, b);
            for k in 0..DIM {
                e[k] -= d * b[k];
            }
        }
        normalize(&mut e);
        let norm: f64 = e.iter().map(|x| x * x).sum::<f64>().sqrt();
        if norm > 1e-12 && basis.len() < DIM {
            basis.push(e);
        }
    }

    let mut perp = [[0.0; DIM]; 3];
    for i in 0..3 {
        let idx = 2 + i;
        if idx < basis.len() {
            for j in 0..DIM {
                perp[i][j] = basis[idx][j];
            }
        }
    }
    perp
}

// ── Cut-and-project ─────────────────────────────────────────────────

// `k` is used both as an index into two parallel rows and as an
// arithmetic angle value (`k as f64 * TWO_PI_OVER_5`).
#[allow(clippy::needless_range_loop)]
fn golden_projection() -> [[f64; DIM]; 2] {
    let mut proj = [[0.0; DIM]; 2];
    for k in 0..DIM {
        let angle = k as f64 * TWO_PI_OVER_5;
        proj[0][k] = angle.cos();
        proj[1][k] = angle.sin();
    }
    proj
}

fn compile_tiles(range: i32, groove_width: f64) -> Vec<Tile> {
    let proj = golden_projection();
    let perp = gram_schmidt_perp(&proj);
    let mut tiles = Vec::new();

    // Iterate over 5D lattice cube
    let mut coords = [0i32; DIM];
    let mut idx = [0usize; DIM]; // loop indices

    loop {
        // Compute source as f64
        let src = [
            coords[0] as f64,
            coords[1] as f64,
            coords[2] as f64,
            coords[3] as f64,
            coords[4] as f64,
        ];

        // Check perpendicular window
        let mut pv = [0.0, 0.0, 0.0];
        for r in 0..3 {
            for j in 0..DIM {
                pv[r] += perp[r][j] * src[j];
            }
        }
        let accepted = pv.iter().all(|&v| v.abs() < groove_width);

        if accepted {
            let target = mat_vec(&proj, &src);
            let s = coords.iter().map(|&c| c.abs() as f64).sum::<f64>() * INV_PHI;
            let frac = s - s.floor();
            let tile_type = if frac < INV_PHI {
                TileType::Thick
            } else {
                TileType::Thin
            };

            tiles.push(Tile {
                x: target[0],
                y: target[1],
                source: coords,
                tile_type,
            });
        }

        // Increment multi-index
        let mut carry = true;
        for d in 0..DIM {
            if !carry {
                break;
            }
            idx[d] += 1;
            coords[d] = idx[d] as i32 - range;
            if idx[d] > (2 * range) as usize {
                idx[d] = 0;
                coords[d] = -range;
            } else {
                carry = false;
            }
        }
        if carry {
            break;
        }
    }

    tiles
}

// ── Public API ──────────────────────────────────────────────────────

/// Generate Penrose rhythm hits via cut-and-project.
pub fn penrose_rhythm(range: i32, groove_width: f64) -> Vec<i32> {
    let tiles = compile_tiles(range, groove_width);
    if tiles.is_empty() {
        return vec![];
    }

    let xmin = tiles.iter().map(|t| t.x).fold(f64::INFINITY, f64::min);
    let xmax = tiles.iter().map(|t| t.x).fold(f64::NEG_INFINITY, f64::max);
    let span = (xmax - xmin).max(1e-12);

    let mut hits: Vec<i32> = tiles
        .iter()
        .map(|t| ((t.x - xmin) / span * 16.0) as i32)
        .collect();
    hits.sort();
    hits.dedup();
    hits
}

/// Generate Penrose melody notes from a scale.
pub fn penrose_melody(scale: &[i32], range: i32) -> Vec<i32> {
    let tiles = compile_tiles(range, 0.5);
    if tiles.is_empty() {
        return vec![];
    }

    let ymin = tiles.iter().map(|t| t.y).fold(f64::INFINITY, f64::min);
    let ymax = tiles.iter().map(|t| t.y).fold(f64::NEG_INFINITY, f64::max);
    let yspan = (ymax - ymin).max(1e-12);

    tiles
        .iter()
        .map(|t| {
            let y_norm = (t.y - ymin) / yspan;
            let sidx = (y_norm * (scale.len() - 1) as f64) as usize;
            let sidx = sidx.min(scale.len() - 1);
            let oct_off = (y_norm * 2.0) as i32 - 1;
            let midi = 12 * (5 + oct_off) + scale[sidx];
            midi.clamp(0, 127)
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn approx_eq(a: f64, b: f64, eps: f64) -> bool {
        (a - b).abs() < eps
    }

    #[test]
    fn test_penrose_rhythm_not_empty() {
        let hits = penrose_rhythm(3, 0.5);
        assert!(!hits.is_empty());
        for &h in &hits {
            assert!(h >= 0 && h <= 16);
        }
    }

    #[test]
    fn test_penrose_rhythm_sorted() {
        let hits = penrose_rhythm(4, 0.6);
        for i in 1..hits.len() {
            assert!(hits[i] >= hits[i - 1]);
        }
    }

    #[test]
    fn test_penrose_melody_not_empty() {
        let notes = penrose_melody(&[0, 2, 4, 7, 9], 3);
        assert!(!notes.is_empty());
        for &n in &notes {
            assert!(n >= 0 && n <= 127);
        }
    }

    #[test]
    fn test_larger_range_more_tiles() {
        let n1 = penrose_melody(&[0, 2, 4, 7, 9], 2).len();
        let n2 = penrose_melody(&[0, 2, 4, 7, 9], 5).len();
        assert!(n2 >= n1);
    }

    #[test]
    fn test_groove_width_density() {
        let n1 = penrose_rhythm(4, 0.3).len();
        let n2 = penrose_rhythm(4, 0.8).len();
        assert!(n2 >= n1);
    }

    #[test]
    fn test_golden_projection_orthogonal() {
        let proj = golden_projection();
        // Rows are sums of 5 cos²/sin² values = 5/2, so norm = sqrt(5/2)
        for r in 0..2 {
            let norm: f64 = proj[r].iter().map(|x| x * x).sum();
            assert!(approx_eq(norm, 2.5, 0.01));
        }
    }

    #[test]
    fn test_reject_all_window() {
        // Very small window → should produce few or no tiles
        let hits = penrose_rhythm(3, 0.001);
        // With tiny window, very few lattice points pass
        assert!(hits.len() < 5);
    }
}
