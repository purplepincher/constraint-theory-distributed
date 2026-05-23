//! World rhythm patterns — 26 patterns: clave, bell, tala, iqa, swing.

/// A rhythm pattern with hit positions within a subdivided cycle.
#[derive(Debug, Clone, PartialEq)]
pub struct RhythmPattern {
    pub name: &'static str,
    pub culture: &'static str,
    pub subdivisions: i32,
    pub hits: &'static [i32],
}

impl RhythmPattern {
    /// Get the number of hits.
    pub fn hit_count(&self) -> usize { self.hits.len() }
}

// ── Pattern database ────────────────────────────────────────────────

static RHYTHMS: &[RhythmPattern] = &[
    // Clave patterns (5)
    RhythmPattern { name: "son_2_3",       culture: "cuban",       subdivisions: 16, hits: &[0,3,6,8,11] },
    RhythmPattern { name: "son_3_2",       culture: "cuban",       subdivisions: 16, hits: &[0,3,6,10,13] },
    RhythmPattern { name: "rumba_2_3",     culture: "cuban",       subdivisions: 16, hits: &[0,3,6,8,12] },
    RhythmPattern { name: "rumba_3_2",     culture: "cuban",       subdivisions: 16, hits: &[0,4,8,10,13] },
    RhythmPattern { name: "bossa_nova",    culture: "brazilian",   subdivisions: 16, hits: &[0,3,6,8,11,14] },

    // Bell patterns (6)
    RhythmPattern { name: "agbadza",       culture: "ewe",         subdivisions: 12, hits: &[0,3,4,6,8,10] },
    RhythmPattern { name: "gahu",          culture: "ewe",         subdivisions: 12, hits: &[0,2,5,6,8,10] },
    RhythmPattern { name: "atsiagbekor",   culture: "ewe",         subdivisions: 12, hits: &[0,2,5,6,8,11] },
    RhythmPattern { name: "kinka",         culture: "ewe",         subdivisions: 12, hits: &[0,3,6,8,11] },
    RhythmPattern { name: "yanvalou",      culture: "west_africa", subdivisions: 16, hits: &[0,3,6,9,12,15] },
    RhythmPattern { name: "iren",          culture: "west_africa", subdivisions: 16, hits: &[0,2,4,6,8,10,12,14] },

    // Indian talas (7)
    RhythmPattern { name: "teental",       culture: "indian",      subdivisions: 16, hits: &[0,4,8,12] },
    RhythmPattern { name: "jhap_tal",      culture: "indian",      subdivisions: 10, hits: &[0,2,5,7] },
    RhythmPattern { name: "rupak",         culture: "indian",      subdivisions: 7,  hits: &[0,3,5] },
    RhythmPattern { name: "ek_tal",        culture: "indian",      subdivisions: 12, hits: &[0,2,4,6,8,10] },
    RhythmPattern { name: "kaharwa",       culture: "indian",      subdivisions: 8,  hits: &[0,4] },
    RhythmPattern { name: "dadra",         culture: "indian",      subdivisions: 6,  hits: &[0,3] },
    RhythmPattern { name: "deepchandi",    culture: "indian",      subdivisions: 14, hits: &[0,3,7,10] },

    // Arabic iqa'at (8)
    RhythmPattern { name: "maqsum",        culture: "arabic",      subdivisions: 8,  hits: &[0,2,4,6] },
    RhythmPattern { name: "baladi",        culture: "arabic",      subdivisions: 8,  hits: &[0,2,4,6] },
    RhythmPattern { name: "saidi",         culture: "arabic",      subdivisions: 8,  hits: &[0,2,4,6] },
    RhythmPattern { name: "malfuf",        culture: "arabic",      subdivisions: 4,  hits: &[0,2] },
    RhythmPattern { name: "fallahi",       culture: "arabic",      subdivisions: 4,  hits: &[0,2] },
    RhythmPattern { name: "sama_i_thaqil", culture: "arabic",      subdivisions: 20, hits: &[0,4,8,12,16] },
    RhythmPattern { name: "aqsaq",         culture: "arabic",      subdivisions: 18, hits: &[0,4,8,12,16] },
    RhythmPattern { name: "dawr_hind",     culture: "arabic",      subdivisions: 14, hits: &[0,4,8,12] },
];

/// Look up a rhythm by name.
pub fn get_rhythm(name: &str) -> Option<&'static RhythmPattern> {
    let key = name.to_lowercase().replace([' ', '-'], "_");
    RHYTHMS.iter().find(|r| r.name == key)
}

/// Get all rhythm patterns.
pub fn all_rhythms() -> Vec<&'static RhythmPattern> {
    RHYTHMS.iter().collect()
}

/// Count of all rhythms.
pub fn rhythm_count() -> usize { RHYTHMS.len() }

/// Compute swing timing from a ratio (0.5=straight, 0.67=triplet, 0.75=dotted).
pub fn swing_ratio(ratio: f64) -> Result<(f64, f64), String> {
    if !(0.25..=0.85).contains(&ratio) {
        return Err("Swing ratio should be between 0.25 and 0.85".into());
    }
    let long = ratio * 2.0;
    let short = (1.0 - ratio) * 2.0;
    let total = long + short;
    Ok(((long / total * 10000.0).round() / 10000.0, (short / total * 10000.0).round() / 10000.0))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_son_clave() {
        let r = get_rhythm("son_2_3").unwrap();
        assert_eq!(r.hit_count(), 5);
        assert_eq!(r.hits[0], 0);
        assert_eq!(r.hits[4], 11);
    }

    #[test]
    fn test_bossa_nova() {
        let r = get_rhythm("bossa_nova").unwrap();
        assert_eq!(r.hit_count(), 6);
    }

    #[test]
    fn test_agbadza() {
        let r = get_rhythm("agbadza").unwrap();
        assert_eq!(r.hit_count(), 6);
        assert_eq!(r.hits[0], 0);
    }

    #[test]
    fn test_teental() {
        let r = get_rhythm("teental").unwrap();
        assert_eq!(r.subdivisions, 16);
        assert_eq!(r.hit_count(), 4);
    }

    #[test]
    fn test_rhythm_count() {
        assert_eq!(rhythm_count(), 26);
    }

    #[test]
    fn test_not_found() {
        assert!(get_rhythm("nonexistent").is_none());
    }

    #[test]
    fn test_swing_triplet() {
        let (long, short) = swing_ratio(0.67).unwrap();
        assert!(long > short);
        assert!((long + short - 1.0).abs() < 0.01);
    }

    #[test]
    fn test_swing_invalid() {
        assert!(swing_ratio(0.1).is_err());
    }
}
