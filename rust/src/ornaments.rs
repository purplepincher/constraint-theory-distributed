//! World music ornaments — meend, gamak, quarter bends, grace notes, murki, shakes.

use std::f64::consts::PI;

/// Curve type for ornaments.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Curve {
    Exponential,
    Logarithmic,
    Linear,
}

/// Indian meend (glide) from `start` to `end` pitch in semitones.
/// Returns `steps + 1` pitch values.
pub fn meend(start: f64, end: f64, steps: i32, curve: Curve) -> Vec<f64> {
    if steps < 1 { return vec![start]; }
    let mut result = Vec::with_capacity((steps + 1) as usize);
    for i in 0..=steps {
        let t = i as f64 / steps as f64;
        let value = match curve {
            Curve::Exponential => start + (end - start) * t * t,
            Curve::Logarithmic => start + (end - start) * (1.0 - (1.0 - t) * (1.0 - t)),
            Curve::Linear => start + (end - start) * t,
        };
        result.push((value * 10000.0).round() / 10000.0);
    }
    result
}

/// Indian gamak (oscillation) around `center` pitch.
/// Returns pitch values simulating rapid oscillation with gentle decay.
pub fn gamak(center: f64, amplitude: f64, speed: f64, cycles: i32) -> Vec<f64> {
    let total_points = (speed * cycles as f64 * 4.0) as usize;
    let mut result = Vec::with_capacity(total_points + 1);
    for i in 0..=total_points {
        let t = i as f64 / total_points.max(1) as f64;
        let decay = 1.0 - t * 0.3;
        let val = center + amplitude * decay * (2.0 * PI * speed * cycles as f64 * t).sin();
        result.push((val * 10000.0).round() / 10000.0);
    }
    result
}

/// Direction for bends.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BendDirection { Up, Down }

/// Arabic quarter-tone bend.
/// Returns a pitch trajectory: smoothstep up, hold, smoothstep down.
pub fn quarter_bend(note: f64, direction: BendDirection, cents: f64, steps: i32) -> Vec<f64> {
    let semitones = cents / 100.0;
    let target = match direction {
        BendDirection::Up => note + semitones,
        BendDirection::Down => note - semitones,
    };
    let steps = steps.max(1);
    let mut traj = Vec::with_capacity(2 * steps as usize + 5);

    // Smoothstep up
    for i in 0..=steps {
        let t = i as f64 / steps as f64;
        let val = t * t * (3.0 - 2.0 * t);
        traj.push(((note + (target - note) * val) * 10000.0).round() / 10000.0);
    }
    // Hold
    for _ in 0..4 {
        traj.push((target * 10000.0).round() / 10000.0);
    }
    // Smoothstep down
    for i in 0..=steps {
        let t = i as f64 / steps as f64;
        let val = t * t * (3.0 - 2.0 * t);
        traj.push(((target + (note - target) * val) * 10000.0).round() / 10000.0);
    }
    traj
}

/// A grace note event.
#[derive(Debug, Clone, PartialEq)]
pub struct GraceEvent {
    pub pitch: f64,
    pub duration_ms: i32,
}

/// Approach type for grace notes.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Approach { Adjacent, DiatonicAbove, DiatonicBelow }

/// Universal grace note approaching `target`.
pub fn grace_note(target: f64, approach: Approach, duration_ms: i32) -> Vec<GraceEvent> {
    let source = match approach {
        Approach::Adjacent => target - 1.0,
        Approach::DiatonicAbove => target + 2.0,
        Approach::DiatonicBelow => target - 2.0,
    };
    vec![
        GraceEvent { pitch: (source * 100.0).round() / 100.0, duration_ms },
        GraceEvent { pitch: (target * 100.0).round() / 100.0, duration_ms: 0 },
    ]
}

/// Indian murki (turn) — rapid alternation between notes.
pub fn murki(notes: &[f64], speed_ms: i32) -> Vec<GraceEvent> {
    if notes.len() < 2 {
        return notes.iter().map(|&n| GraceEvent { pitch: (n * 100.0).round() / 100.0, duration_ms: speed_ms }).collect();
    }
    let mut result = Vec::new();
    for _ in 0..2 {
        for &n in notes {
            result.push(GraceEvent { pitch: (n * 100.0).round() / 100.0, duration_ms: speed_ms });
        }
        for &n in notes[1..notes.len()-1].iter().rev() {
            result.push(GraceEvent { pitch: (n * 100.0).round() / 100.0, duration_ms: speed_ms });
        }
    }
    result
}

/// Jazz shake — rapid trill around `note`.
pub fn shakes(note: f64, speed: f64, amplitude: f64) -> Vec<f64> {
    let points = (speed * 8.0) as usize;
    let mut result = Vec::with_capacity(points);
    for i in 0..points {
        let t = i as f64 / (points - 1).max(1) as f64;
        let val = note + amplitude * (2.0 * PI * speed * t).sin();
        result.push((val * 10000.0).round() / 10000.0);
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    fn approx_eq(a: f64, b: f64, eps: f64) -> bool { (a - b).abs() < eps }

    #[test]
    fn test_meend_exponential() {
        let out = meend(0.0, 12.0, 20, Curve::Exponential);
        assert_eq!(out.len(), 21);
        assert!(approx_eq(out[0], 0.0, 0.001));
        assert!(approx_eq(out[20], 12.0, 0.001));
        assert!(out[10] < 6.0); // slow start
    }

    #[test]
    fn test_meend_linear() {
        let out = meend(0.0, 10.0, 10, Curve::Linear);
        assert!(approx_eq(out[5], 5.0, 0.001));
    }

    #[test]
    fn test_meend_logarithmic() {
        let out = meend(0.0, 10.0, 10, Curve::Logarithmic);
        assert!(out[5] > 5.0); // fast start
    }

    #[test]
    fn test_gamak() {
        let out = gamak(5.0, 0.5, 6.0, 3);
        assert!(!out.is_empty());
        assert!(out[0] > 4.0 && out[0] < 6.0);
    }

    #[test]
    fn test_quarter_bend_up() {
        let out = quarter_bend(5.0, BendDirection::Up, 50.0, 10);
        assert!(approx_eq(out[0], 5.0, 0.001));
        assert!(approx_eq(*out.last().unwrap(), 5.0, 0.001));
    }

    #[test]
    fn test_quarter_bend_down() {
        let out = quarter_bend(5.0, BendDirection::Down, 50.0, 10);
        assert!(approx_eq(out[0], 5.0, 0.001));
    }

    #[test]
    fn test_shakes() {
        let out = shakes(5.0, 8.0, 0.3);
        assert!(!out.is_empty());
        let min_val = out.iter().cloned().fold(f64::INFINITY, f64::min);
        let max_val = out.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        assert!(min_val < 5.0);
        assert!(max_val > 5.0);
    }

    #[test]
    fn test_grace_note_adjacent() {
        let events = grace_note(60.0, Approach::Adjacent, 30);
        assert_eq!(events.len(), 2);
        assert_eq!(events[0].pitch, 59.0);
        assert_eq!(events[0].duration_ms, 30);
        assert_eq!(events[1].pitch, 60.0);
        assert_eq!(events[1].duration_ms, 0);
    }

    #[test]
    fn test_murki() {
        let events = murki(&[60.0, 62.0, 64.0], 80);
        assert!(!events.is_empty());
        // Forward and back, twice: [60,62,64] + [62] + [60,62,64] + [62] = 8 events
        assert!(events.len() >= 8);
    }
}
