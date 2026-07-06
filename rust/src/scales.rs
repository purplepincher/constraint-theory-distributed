//! World music scales — 36 scales across Indian, Arabic, East Asian, African, and other cultures.

use std::fmt;
// use std::str::FromStr; // not needed without strum

/// A world music scale with optional metadata.
#[derive(Debug, Clone, PartialEq)]
pub struct WorldScale {
    pub name: &'static str,
    pub culture: &'static str,
    pub notes: &'static [i32],
    pub vadi: Option<i32>,
    pub samvadi: Option<i32>,
    pub rasa: Option<&'static str>,
}

impl WorldScale {
    /// Expand this scale to MIDI note numbers across `octave_range` octaves from `root`.
    pub fn to_midi(&self, root: i32, octave_range: i32) -> Vec<i32> {
        let mut midi_notes = Vec::new();
        for octave in 0..octave_range {
            let offset = octave * 12;
            for &n in self.notes {
                let rounded = n; // notes are already integer semitones
                let midi = root + rounded + offset;
                if (0..=127).contains(&midi) && !midi_notes.contains(&midi) {
                    midi_notes.push(midi);
                }
            }
        }
        midi_notes.sort();
        midi_notes
    }
}

impl fmt::Display for WorldScale {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} ({}: {:?})", self.name, self.culture, self.notes)
    }
}

// ── Scale definitions ───────────────────────────────────────────────

macro_rules! scale {
    ($name:expr, $culture:expr, [$($n:expr),*]) => {
        WorldScale {
            name: $name,
            culture: $culture,
            notes: &[$($n),*],
            vadi: None,
            samvadi: None,
            rasa: None,
        }
    };
    ($name:expr, $culture:expr, [$($n:expr),*], vadi=$v:expr, samvadi=$sv:expr, rasa=$r:expr) => {
        WorldScale {
            name: $name,
            culture: $culture,
            notes: &[$($n),*],
            vadi: Some($v),
            samvadi: Some($sv),
            rasa: Some($r),
        }
    };
}

static SCALES: &[WorldScale] = &[
    // Indian Ragas (10)
    scale!(
        "bhairavi",
        "indian",
        [0, 1, 3, 5, 7, 8, 10],
        vadi = 1,
        samvadi = 5,
        rasa = "devotional"
    ),
    scale!(
        "yaman",
        "indian",
        [0, 2, 4, 6, 7, 9, 11],
        vadi = 0,
        samvadi = 4,
        rasa = "romantic"
    ),
    scale!(
        "darbari",
        "indian",
        [0, 2, 3, 5, 7, 8, 10],
        vadi = 3,
        samvadi = 7,
        rasa = "solemn"
    ),
    scale!(
        "malkauns",
        "indian",
        [0, 2, 4, 6, 8, 10],
        vadi = 2,
        samvadi = 6,
        rasa = "meditative"
    ),
    scale!(
        "bageshri",
        "indian",
        [0, 2, 3, 5, 7, 9, 10],
        vadi = 2,
        samvadi = 7,
        rasa = "longing"
    ),
    scale!(
        "todi",
        "indian",
        [0, 1, 3, 5, 7, 8, 11],
        vadi = 3,
        samvadi = 7,
        rasa = "pathos"
    ),
    scale!(
        "bhairav",
        "indian",
        [0, 1, 4, 5, 7, 8, 11],
        vadi = 4,
        samvadi = 8,
        rasa = "solemn"
    ),
    scale!(
        "kafi",
        "indian",
        [0, 2, 3, 5, 7, 9, 10],
        vadi = 3,
        samvadi = 7,
        rasa = "playful"
    ),
    scale!(
        "bilawal",
        "indian",
        [0, 2, 4, 5, 7, 9, 11],
        vadi = 4,
        samvadi = 0,
        rasa = "joyful"
    ),
    scale!(
        "asavari",
        "indian",
        [0, 2, 3, 5, 7, 8, 10],
        vadi = 3,
        samvadi = 7,
        rasa = "melancholy"
    ),
    // Arabic / Turkish Maqamat (10) — quarter-tone notes rounded to nearest semitone
    scale!("rast", "arabic", [0, 2, 4, 5, 7, 9, 11]),
    scale!("bayati", "arabic", [0, 2, 4, 5, 7, 9, 10]),
    scale!("hijaz", "arabic", [0, 1, 4, 5, 7, 8, 11]),
    scale!("sikah", "arabic", [0, 2, 4, 5, 7, 9, 11]),
    scale!("nahawand", "arabic", [0, 2, 3, 5, 7, 8, 11]),
    scale!("kurd", "arabic", [0, 1, 3, 5, 7, 8, 10]),
    scale!("ajam", "arabic", [0, 2, 4, 5, 7, 9, 11]),
    scale!("saba", "arabic", [0, 1, 3, 4, 6, 7, 10]),
    scale!("huzam", "arabic", [0, 2, 4, 5, 7, 9, 10]),
    scale!("nakriz", "arabic", [0, 2, 3, 5, 7, 8, 11]),
    // East Asian Pentatonic (10)
    scale!("in_scale", "japanese", [0, 2, 3, 7, 8]),
    scale!("yo_scale", "japanese", [0, 2, 5, 7, 9]),
    scale!("hirajoshi", "japanese", [0, 2, 3, 7, 8]),
    scale!("kumoi", "japanese", [0, 2, 3, 7, 9]),
    scale!("gong_mode", "chinese", [0, 2, 4, 7, 9]),
    scale!("shang_mode", "chinese", [0, 2, 4, 7, 9]),
    scale!("jiao_mode", "chinese", [0, 2, 5, 7, 10]),
    scale!("zhi_mode", "chinese", [0, 2, 5, 7, 10]),
    scale!("yu_mode", "chinese", [0, 3, 5, 7, 10]),
    scale!("pentatonic_major", "east_asian", [0, 2, 4, 7, 9]),
    // African Scales (6)
    scale!("ewe_standard", "ewe", [0, 2, 4, 5, 7, 9, 11]),
    scale!("pentatonic_african", "african", [0, 2, 3, 7, 8]),
    scale!("zimbabwe_mbira", "shona", [0, 3, 5, 7, 8, 10]),
    scale!("amadinda_scale", "buganda", [0, 2, 4, 5, 7, 9]),
    scale!("manden_scale", "manden", [0, 2, 4, 6, 7, 9, 11]),
    scale!("tigre_scale", "tigre", [0, 1, 3, 5, 7, 8, 10]),
];

/// Look up a scale by name (case-insensitive).
pub fn get_scale(name: &str) -> Option<&'static WorldScale> {
    let key = name.to_lowercase().replace([' ', '-'], "_");
    SCALES.iter().find(|s| s.name == key)
}

/// Return all scale names, optionally filtered by culture.
pub fn list_scales(culture: Option<&str>) -> Vec<&'static str> {
    let mut names: Vec<_> = match culture {
        Some(c) => SCALES
            .iter()
            .filter(|s| s.culture == c)
            .map(|s| s.name)
            .collect(),
        None => SCALES.iter().map(|s| s.name).collect(),
    };
    names.sort();
    names
}

/// Iterator over all scales.
pub fn all_scales() -> impl Iterator<Item = &'static WorldScale> {
    SCALES.iter()
}

/// Count of all scales.
pub fn scale_count() -> usize {
    SCALES.len()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_scale_bhairavi() {
        let s = get_scale("bhairavi").unwrap();
        assert_eq!(s.notes, [0, 1, 3, 5, 7, 8, 10]);
        assert_eq!(s.vadi, Some(1));
        assert_eq!(s.samvadi, Some(5));
        assert_eq!(s.rasa, Some("devotional"));
    }

    #[test]
    fn test_case_insensitive() {
        assert!(get_scale("Bhairavi").is_some());
        assert!(get_scale("BHAIravI").is_some());
    }

    #[test]
    fn test_not_found() {
        assert!(get_scale("nonexistent").is_none());
    }

    #[test]
    fn test_scale_count() {
        assert_eq!(scale_count(), 36);
    }

    #[test]
    fn test_culture_filter_indian() {
        let indian = list_scales(Some("indian"));
        assert_eq!(indian.len(), 10);
    }

    #[test]
    fn test_culture_filter_arabic() {
        let arabic = list_scales(Some("arabic"));
        assert_eq!(arabic.len(), 10);
    }

    #[test]
    fn test_to_midi_yaman() {
        let s = get_scale("yaman").unwrap();
        let midi = s.to_midi(60, 2);
        assert_eq!(midi[0], 60);
        assert_eq!(midi[1], 62);
        assert_eq!(midi[2], 64);
        assert!(midi.len() >= 7);
    }

    #[test]
    fn test_display() {
        let s = get_scale("bhairavi").unwrap();
        let display = format!("{}", s);
        assert!(display.contains("bhairavi"));
    }

    #[test]
    fn test_all_cultures_present() {
        let cultures: Vec<_> = all_scales().map(|s| s.culture).collect();
        assert!(cultures.contains(&"indian"));
        assert!(cultures.contains(&"arabic"));
        assert!(cultures.contains(&"japanese"));
        assert!(cultures.contains(&"chinese"));
        assert!(cultures.contains(&"ewe"));
        assert!(cultures.contains(&"african"));
    }
}
