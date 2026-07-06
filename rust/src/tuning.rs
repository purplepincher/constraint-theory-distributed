//! Tuning systems — equal temperament, just intonation, shruti, quarter-tone, pentatonic, meantone, pythagorean.

const CENTS_FACTOR: f64 = 1200.0;

/// Convert a frequency ratio to cents.
pub fn ratio_to_cents(ratio: f64) -> f64 {
    CENTS_FACTOR * ratio.log2()
}

/// A tuning system that generates cent offsets for pitch degrees.
#[derive(Debug, Clone)]
pub struct TuningSystem {
    pub name: &'static str,
    pub divisions: usize,
    generator: fn(i32) -> f64,
}

impl TuningSystem {
    /// Get cents for a specific degree.
    pub fn cents(&self, degree: i32) -> f64 {
        (self.generator)(degree)
    }

    /// Generate all cent values.
    pub fn all_cents(&self) -> Vec<f64> {
        (0..self.divisions as i32).map(|i| self.cents(i)).collect()
    }

    /// Snap `note_cents` to the nearest pitch in this tuning.
    /// If `epsilon > 0` and the nearest is farther than epsilon, return note_cents unchanged.
    pub fn snap(&self, note_cents: f64, epsilon: f64) -> f64 {
        let note_wrapped = note_cents % 1200.0;
        let mut best_dist = f64::MAX;
        let mut best_val = 0.0;
        for i in 0..self.divisions {
            let c = self.cents(i as i32) % 1200.0;
            let diff = (c - note_wrapped)
                .abs()
                .min(1200.0 - (c - note_wrapped).abs());
            if diff < best_dist {
                best_dist = diff;
                best_val = c;
            }
        }
        if epsilon > 0.0 && best_dist > epsilon {
            note_cents
        } else {
            best_val
        }
    }
}

// ── Generator functions ─────────────────────────────────────────────

fn gen_equal_12(degree: i32) -> f64 {
    degree as f64 * (1200.0 / 12.0)
}

fn gen_just(degree: i32) -> f64 {
    let ratios = [
        1.0,
        16.0 / 15.0,
        9.0 / 8.0,
        6.0 / 5.0,
        5.0 / 4.0,
        4.0 / 3.0,
        45.0 / 32.0,
        3.0 / 2.0,
        8.0 / 5.0,
        5.0 / 3.0,
        9.0 / 5.0,
        15.0 / 8.0,
    ];
    if (0..12).contains(&degree) {
        ratio_to_cents(ratios[degree as usize])
    } else {
        0.0
    }
}

fn gen_shruti(degree: i32) -> f64 {
    let ratios = [
        1.0,
        256.0 / 243.0,
        16.0 / 15.0,
        10.0 / 9.0,
        9.0 / 8.0,
        32.0 / 27.0,
        6.0 / 5.0,
        5.0 / 4.0,
        81.0 / 64.0,
        4.0 / 3.0,
        27.0 / 20.0,
        45.0 / 32.0,
        729.0 / 512.0,
        3.0 / 2.0,
        128.0 / 81.0,
        8.0 / 5.0,
        5.0 / 3.0,
        27.0 / 16.0,
        16.0 / 9.0,
        9.0 / 5.0,
        15.0 / 8.0,
        243.0 / 128.0,
    ];
    if (0..22).contains(&degree) {
        ratio_to_cents(ratios[degree as usize])
    } else {
        0.0
    }
}

fn gen_quarter_24(degree: i32) -> f64 {
    degree as f64 * 50.0
}
fn gen_penta_5(degree: i32) -> f64 {
    degree as f64 * 240.0
}

fn gen_meantone(degree: i32) -> f64 {
    // Computed on first call, cached in static
    use std::sync::OnceLock;
    static NOTES: OnceLock<Vec<f64>> = OnceLock::new();
    let notes = NOTES.get_or_init(|| {
        let fifth = 1200.0 * 5.0_f64.powf(0.25).log2();
        let mut n = vec![0.0];
        let mut acc = 0.0;
        for _ in 0..11 {
            acc += fifth;
            acc %= 1200.0;
            n.push(acc);
        }
        n.sort_by(|a, b| a.partial_cmp(b).unwrap());
        n
    });
    if (0..12).contains(&degree) {
        notes[degree as usize]
    } else {
        0.0
    }
}

fn gen_pythagorean(degree: i32) -> f64 {
    use std::sync::OnceLock;
    static NOTES: OnceLock<Vec<f64>> = OnceLock::new();
    let notes = NOTES.get_or_init(|| {
        let fifth = 1200.0_f64 * (3.0_f64 / 2.0_f64).log2();
        let mut n = vec![0.0];
        let mut acc = 0.0;
        for _ in 0..11 {
            acc += fifth;
            acc %= 1200.0;
            n.push(acc);
        }
        n.sort_by(|a, b| a.partial_cmp(b).unwrap());
        n
    });
    if (0..12).contains(&degree) {
        notes[degree as usize]
    } else {
        0.0
    }
}

// ── Pre-built tuning systems ────────────────────────────────────────

pub fn equal_temperament() -> TuningSystem {
    TuningSystem {
        name: "equal_temperament",
        divisions: 12,
        generator: gen_equal_12,
    }
}
pub fn just_intonation() -> TuningSystem {
    TuningSystem {
        name: "just_intonation",
        divisions: 12,
        generator: gen_just,
    }
}
pub fn shruti_22() -> TuningSystem {
    TuningSystem {
        name: "shruti_22",
        divisions: 22,
        generator: gen_shruti,
    }
}
pub fn quarter_tone_24() -> TuningSystem {
    TuningSystem {
        name: "quarter_tone_24",
        divisions: 24,
        generator: gen_quarter_24,
    }
}
pub fn pentatonic_5() -> TuningSystem {
    TuningSystem {
        name: "pentatonic_5",
        divisions: 5,
        generator: gen_penta_5,
    }
}
pub fn meantone() -> TuningSystem {
    TuningSystem {
        name: "meantone",
        divisions: 12,
        generator: gen_meantone,
    }
}
pub fn pythagorean() -> TuningSystem {
    TuningSystem {
        name: "pythagorean",
        divisions: 12,
        generator: gen_pythagorean,
    }
}

/// Get all 7 tuning systems.
pub fn all_tuning_systems() -> Vec<TuningSystem> {
    vec![
        equal_temperament(),
        just_intonation(),
        shruti_22(),
        quarter_tone_24(),
        pentatonic_5(),
        meantone(),
        pythagorean(),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    fn approx_eq(a: f64, b: f64, eps: f64) -> bool {
        (a - b).abs() < eps
    }

    #[test]
    fn test_equal_temperament() {
        let et = equal_temperament();
        assert_eq!(et.divisions, 12);
        assert!(approx_eq(et.cents(0), 0.0, 0.01));
        assert!(approx_eq(et.cents(1), 100.0, 0.01));
        assert!(approx_eq(et.cents(7), 700.0, 0.01));
    }

    #[test]
    fn test_just_intonation() {
        let ji = just_intonation();
        assert!(approx_eq(ji.cents(0), 0.0, 0.01));
        assert!(approx_eq(ji.cents(4), 386.31, 0.1)); // 5/4
        assert!(approx_eq(ji.cents(7), 701.96, 0.1)); // 3/2
    }

    #[test]
    fn test_shruti_22() {
        let sh = shruti_22();
        assert_eq!(sh.divisions, 22);
        assert!(approx_eq(sh.cents(13), 701.96, 0.1)); // Pa
    }

    #[test]
    fn test_quarter_tone_24() {
        let qt = quarter_tone_24();
        assert!(approx_eq(qt.cents(1), 50.0, 0.01));
        assert!(approx_eq(qt.cents(12), 600.0, 0.01));
    }

    #[test]
    fn test_pentatonic_5() {
        let p = pentatonic_5();
        assert!(approx_eq(p.cents(1), 240.0, 0.01));
    }

    #[test]
    fn test_pythagorean() {
        let py = pythagorean();
        let fifth = py.cents(7);
        assert!(fifth > 700.0 && fifth < 705.0);
    }

    #[test]
    fn test_meantone() {
        let mt = meantone();
        let fifth = mt.cents(7);
        assert!(fifth > 695.0 && fifth < 700.0);
    }

    #[test]
    fn test_snap() {
        let et = equal_temperament();
        let snapped = et.snap(99.5, 0.0);
        assert!(approx_eq(snapped, 100.0, 0.01));
    }

    #[test]
    fn test_snap_with_epsilon() {
        let et = equal_temperament();
        let no_snap = et.snap(95.0, 2.0);
        assert!(approx_eq(no_snap, 95.0, 0.01));
    }

    #[test]
    fn test_all_cents() {
        let et = equal_temperament();
        let cents = et.all_cents();
        assert_eq!(cents.len(), 12);
        assert!(approx_eq(cents[11], 1100.0, 0.01));
    }

    #[test]
    fn test_ratio_to_cents() {
        assert!(approx_eq(ratio_to_cents(2.0), 1200.0, 0.01));
        assert!(approx_eq(ratio_to_cents(1.0), 0.0, 0.01));
    }

    #[test]
    fn test_all_tuning_systems_count() {
        assert_eq!(all_tuning_systems().len(), 7);
    }
}
