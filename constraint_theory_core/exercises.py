"""
Exercise generator for constraint-theory-core.

Produces constrained composition exercises for classroom use, covering
species counterpoint, voice leading, harmonic constraints, and rhythmic
constraints — all grounded in the geometric and algebraic primitives of
the package (Eisenstein lattices, Laman rigidity, holonomy, etc.).

Public API
----------
>>> from constraint_theory_core.exercises import generate_exercise
>>> ex = generate_exercise("species_counterpoint", "beginner", seed=42)
>>> print(ex["instructions"])
"""

from __future__ import annotations

import random
import json
from dataclasses import dataclass, asdict
from typing import Any

# ---------------------------------------------------------------------------
# Supported enums (kept lightweight — no enum import needed)
# ---------------------------------------------------------------------------

TOPICS = ("species_counterpoint", "voice_leading", "harmonic_constraints", "rhythmic_constraints")
DIFFICULTIES = ("beginner", "intermediate", "advanced")

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Exercise:
    """A single constrained-composition exercise."""

    topic: str
    difficulty: str
    instructions: str
    starting_notes: list[dict[str, Any]]
    constraints: list[str]
    solution: dict[str, Any]
    scoring_rubric: dict[str, int]
    seed: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pick(rng: random.Random, seq: list):
    return rng.choice(seq)


def _species_counterpoint_beginner(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Write a first-species counterpoint above the given cantus firmus using "
                "only consonant intervals (unison, 3rd, 5th, 6th, octave). The cantus firmus "
                "is 8 notes long in the key of C major, ♩=72. Map each interval choice onto "
                "the Eisenstein A₂ lattice: consonant intervals must land within the safe "
                "threshold (error < SAFE_THRESHOLD from a lattice snap point)."
            ),
            "starting_notes": [
                {"voice": "cantus firmus", "pitches": ["C4", "D4", "E4", "F4", "E4", "D4", "C4"]},
            ],
            "constraints": [
                "Use only consonant intervals (1, 3, 5, 6, 8) against the cantus firmus.",
                "Each counterpoint pitch must snap to an A₂ lattice point with is_safe(err) == True.",
                "No parallel perfect fifths or octaves between successive sonorities.",
                "Begin and end on a perfect consonance (unison, 5th, or octave).",
            ],
            "solution": {
                "counterpoint": ["C5", "E5", "G4", "A4", "G4", "E5", "C5"],
                "intervals": [8, 6, 5, 6, 5, 6, 8],
                "explanation": (
                    "All intervals are consonant; each pitch-pair vector snaps cleanly "
                    "to the A₂ lattice with safe error. No parallel 5ths/octaves."
                ),
            },
            "rubric": {"consonance": 25, "lattice_snap": 25, "no_parallels": 25, "start_end": 25},
        },
        {
            "instructions": (
                "Complete a two-voice first-species exercise below the given cantus firmus. "
                "The upper voice (cantus firmus) is provided; compose the lower voice note-by-note "
                "ensuring every interval is consonant and maps within the A₂ covering radius."
            ),
            "starting_notes": [
                {"voice": "cantus firmus", "pitches": ["G4", "A4", "B4", "C5", "B4", "A4", "G4"]},
            ],
            "constraints": [
                "All intervals against the cantus firmus must be consonant.",
                "Each lower-voice pitch must satisfy is_safe(err) when snapped to the A₂ lattice.",
                "Avoid parallel perfect consonances.",
                "The final interval must be an octave or unison.",
            ],
            "solution": {
                "counterpoint": ["G3", "F3", "D4", "C4", "D4", "F3", "G3"],
                "intervals": [8, 6, 5, 6, 5, 6, 8],
                "explanation": "Lower voice stays consonant, snaps safely, and resolves to octave.",
            },
            "rubric": {"consonance": 25, "lattice_snap": 25, "no_parallels": 25, "resolution": 25},
        },
        {
            "instructions": (
                "Identify which of the following intervals are 'safe' on the Eisenstein A₂ lattice "
                "by computing snap(x, y) for each pitch difference and checking is_safe(err). "
                "Express each interval as a semitone difference and classify it."
            ),
            "starting_notes": [
                {"voice": "reference", "pitches": ["C4"]},
                {"voice": "test", "pitches": ["E4", "F#4", "G4", "A4", "B4", "C5"]},
            ],
            "constraints": [
                "Compute the vector difference (in semitones) between C4 and each test pitch.",
                "Use snap() to find the nearest A₂ lattice point.",
                "Classify each as 'safe' or 'unsafe' using is_safe().",
                "Report the covering-radius error for each.",
            ],
            "solution": {
                "intervals_semitones": [4, 6, 7, 9, 11, 12],
                "safe": [False, True, True, True, False, True],
                "explanation": "Major 3rd (4) and major 7th (11) fall outside safe threshold; others are safe.",
            },
            "rubric": {"snap_accuracy": 30, "safety_classification": 30, "error_report": 20, "explanation": 20},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="species_counterpoint", difficulty="beginner", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _species_counterpoint_intermediate(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Compose a second-species counterpoint (2:1 rhythmic ratio) above the cantus firmus. "
                "Strong beats must be consonant; weak beats may use passing tones that are dissonant "
                "but must still snap within the A₂ covering radius. Verify holonomy consistency "
                "around every cycle of three successive intervals."
            ),
            "starting_notes": [
                {"voice": "cantus firmus", "pitches": ["D4", "F4", "A4", "G4", "F4", "E4", "D4"]},
            ],
            "constraints": [
                "Strong beats: consonant intervals only, is_safe() must be True.",
                "Weak beats: passing dissonances allowed, but must satisfy covering_radius() tolerance.",
                "Verify holonomy_product() == identity for every 3-interval cycle.",
                "No parallel fifths/octaves on successive strong beats.",
            ],
            "solution": {
                "counterpoint": ["D5", "E5", "F5", "G5", "A4", "B4", "C5", "B4", "A4", "G4", "F4", "E4", "D4", "D4"],
                "explanation": "Strong beats are consonant; weak beats are passing tones within covering radius.",
            },
            "rubric": {"strong_beat_consonance": 25, "weak_beat_tolerance": 20, "holonomy": 30, "no_parallels": 25},
        },
        {
            "instructions": (
                "Write a third-species counterpoint (4:1) against the given cantus firmus. "
                "At least two notes per group of four must be consonant. Verify that the "
                "Laman-type constraint (2n-3) is satisfied: for n sounding notes, there must "
                "be at least 2n-3 independent intervallic constraints."
            ),
            "starting_notes": [
                {"voice": "cantus firmus", "pitches": ["C4", "D4", "E4", "F4", "G4", "A4", "G4", "F4", "E4", "D4", "C4"]},
            ],
            "constraints": [
                "At least 2 of every 4 counterpoint notes must form consonant intervals.",
                "All pitches must snap to the A₂ lattice within SAFE_THRESHOLD.",
                "Laman constraint: 2n - 3 independent constraints for n notes.",
                "Resolve to a perfect consonance at the final cadence.",
            ],
            "solution": {
                "counterpoint": ["E5", "D5", "C5", "D5", "E5", "F5", "G5", "F5", "E5", "D5", "C5", "B4", "A4", "B4", "C5", "B4", "A4", "G4", "F4", "E4", "D4", "C5"],
                "explanation": "4:1 motion with consonant anchors; Laman count verified.",
            },
            "rubric": {"consonant_density": 25, "laman_constraint": 30, "lattice_snap": 20, "cadence": 25},
        },
        {
            "instructions": (
                "Compose a fourth-species counterpoint (suspension chain) above the cantus firmus. "
                "Each suspension must resolve down by step. Verify the resolution interval "
                "snaps cleanly on the A₂ lattice. Model the suspension-resolution pairs as "
                "a Laman graph: each pair contributes 2 independent constraints."
            ),
            "starting_notes": [
                {"voice": "cantus firmus", "pitches": ["G3", "A3", "B3", "C4", "D4", "C4", "B3", "A3", "G3"]},
            ],
            "constraints": [
                "Syncopated rhythm: counterpoint ties across the bar, resolving on the weak beat.",
                "Suspension must be dissonant; resolution must be consonant.",
                "Each resolution interval must be A₂-safe.",
                "No two consecutive identical suspensions (7-6, 4-3 alternating encouraged).",
            ],
            "solution": {
                "counterpoint": ["G4", "G4", "A4", "A4", "B4", "B4", "C5", "C5", "D5", "C5", "B4", "A4", "G4", "G4", "G4", "G4", "G4"],
                "explanation": "Suspension chain 7-6, 4-3 alternating with clean resolutions.",
            },
            "rubric": {"suspension_dissonance": 25, "resolution_consonance": 25, "lattice_snap": 25, "variety": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="species_counterpoint", difficulty="intermediate", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _species_counterpoint_advanced(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Compose a complete five-voice motet fragment (8 measures) adhering to strict "
                "species-counterpoint rules across all voice pairs. Verify global holonomic "
                "consistency: for every fundamental cycle in the voice-pair graph, the holonomy "
                "product must be the identity. The voice-pair constraint graph must be Laman-rigid "
                "(is_laman() == True for the corresponding Henneberg construction)."
            ),
            "starting_notes": [
                {"voice": "soprano", "pitches": ["G4"]},
                {"voice": "alto", "pitches": ["D4"]},
                {"voice": "tenor", "pitches": ["B3"]},
                {"voice": "baritone", "pitches": ["G3"]},
                {"voice": "bass", "pitches": ["G2"]},
            ],
            "constraints": [
                "All adjacent voice pairs must use consonant intervals on strong beats.",
                "Global holonomic consistency: verify_consistency() must pass for all cycles.",
                "Voice-pair graph must satisfy is_laman() with 2n-3 edges.",
                "No hidden parallels; all pitch pairs A₂-safe.",
                "Include at least one cadential suspension in the final two measures.",
            ],
            "solution": {
                "voices": {
                    "soprano": ["G4", "A4", "B4", "C5", "D5", "C5", "B4", "A4", "G4"],
                    "alto": ["D4", "E4", "F4", "G4", "A4", "G4", "F4", "E4", "D4"],
                    "tenor": ["B3", "C4", "D4", "E4", "F4", "E4", "D4", "C4", "B3"],
                    "baritone": ["G3", "A3", "B3", "C4", "D4", "C4", "B3", "A3", "G3"],
                    "bass": ["G2", "A2", "B2", "C3", "D3", "C3", "B2", "A2", "G2"],
                },
                "holonomy_cycles_pass": True,
                "laman_rigid": True,
                "explanation": "All voice pairs consonant; holonomy verified; Laman-rigid constraint graph.",
            },
            "rubric": {"pairwise_consonance": 20, "holonomy": 25, "laman_rigidity": 25, "no_parallels": 15, "cadence": 15},
        },
        {
            "instructions": (
                "Build a three-voice invertible counterpoint at the octave. The subject in the "
                "middle voice must work when inverted to the top or bottom voice. Verify that "
                "the permutation of voices preserves holonomic consistency (cycle_holonomy() "
                "must be identity for all fundamental cycles under each voice permutation). "
                "Additionally verify Laman rigidity of the three-voice constraint graph."
            ),
            "starting_notes": [
                {"voice": "voice_1", "pitches": ["C4", "D4", "E4", "F4", "G4", "F4", "E4", "D4", "C4"]},
                {"voice": "voice_2", "pitches": ["G3"]},
                {"voice": "voice_3", "pitches": ["E3"]},
            ],
            "constraints": [
                "Compose voice_2 and voice_3 against the given subject (voice_1).",
                "When voice_1 and voice_2 swap octaves, all intervals must remain consonant.",
                "Verify holonomy consistency under voice permutation.",
                "Constraint graph (3 voices, 3 pairs) must be Laman: 2·3-3 = 3 independent edges.",
            ],
            "solution": {
                "voice_2": ["G3", "A3", "B3", "C4", "D4", "C4", "B3", "A3", "G3"],
                "voice_3": ["E3", "F3", "G3", "A3", "B3", "A3", "G3", "F3", "E3"],
                "inverted_consonant": True,
                "holonomy_permutation_identity": True,
                "explanation": "Invertible at the octave; holonomy preserved under swap.",
            },
            "rubric": {"invertibility": 25, "consonance_original": 20, "consonance_inverted": 20, "holonomy": 20, "laman": 15},
        },
        {
            "instructions": (
                "Compose a double canon (two subjects, four voices) of 6 measures. Each subject "
                "appears in two voices at different temporal offsets. Model the full constraint "
                "network as a Laman graph (4 voices → 2·4-3 = 5 independent constraint edges). "
                "Use verify_consistency() to ensure holonomy for all fundamental cycles. "
                "Map each canonic interval onto the A₂ lattice; report snap errors."
            ),
            "starting_notes": [
                {"voice": "soprano", "pitches": ["C5", "D5", "E5", "F5", "E5", "D5", "C5"]},
                {"voice": "alto", "pitches": ["G4"]},
                {"voice": "tenor", "pitches": ["C4", "B3", "A3", "G3", "A3", "B3", "C4"]},
                {"voice": "bass", "pitches": ["E3"]},
            ],
            "constraints": [
                "Alto enters 2 beats after soprano at the octave (subject 1).",
                "Bass enters 2 beats after tenor at the 12th (compound 5th, subject 2).",
                "All simultaneous intervals must be A₂-safe.",
                "Laman constraint: 5 independent voice-pair constraints.",
                "Holonomy verification on all fundamental cycles of the 4-voice graph.",
            ],
            "solution": {
                "alto": ["—", "—", "C5", "D5", "E5", "F5", "E5", "D5", "C5"],
                "bass": ["—", "—", "C4", "B3", "A3", "G3", "A3", "B3", "C4"],
                "laman_edges": 5,
                "holonomy_pass": True,
                "explanation": "Double canon with canonic entries; Laman-rigid and holonomy-consistent.",
            },
            "rubric": {"canonic_accuracy": 25, "consonance": 20, "laman": 20, "holonomy": 20, "snap_report": 15},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="species_counterpoint", difficulty="advanced", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _voice_leading_beginner(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Connect two triads (C major → F major) with smooth voice leading. Each voice "
                "should move by the smallest interval possible. Verify each voice's movement "
                "snaps to an A₂ lattice point with safe error. Report the total voice-leading "
                "distance as the sum of squared semitone movements."
            ),
            "starting_notes": [
                {"voice": "soprano", "chord": "C major", "pitches": ["E4"]},
                {"voice": "alto", "chord": "C major", "pitches": ["C4"]},
                {"voice": "tenor", "chord": "C major", "pitches": ["G3"]},
                {"voice": "bass", "chord": "C major", "pitches": ["C3"]},
            ],
            "constraints": [
                "Move to an F-major triad (F-A-C voicing).",
                "Each voice moves ≤ 3 semitones.",
                "All movements must be A₂-safe (is_safe() == True after snap).",
                "No voice crossings.",
            ],
            "solution": {
                "target": {"soprano": "F4", "alto": "C4", "tenor": "A3", "bass": "F3"},
                "movements": [1, 0, 2, 5],
                "total_distance_sq": 30,
                "explanation": "Smooth voice leading with minimal movement; all A₂-safe.",
            },
            "rubric": {"minimal_movement": 30, "no_crossings": 20, "lattice_snap": 25, "correct_target": 25},
        },
        {
            "instructions": (
                "Given a sequence of four triads (C → Am → F → G), find voice-leading paths "
                "between each successive pair that minimize total semitone distance. For each "
                "transition, verify A₂-safe snapping of voice movements."
            ),
            "starting_notes": [
                {"voice": "all", "chords": ["C major", "A minor", "F major", "G major"]},
            ],
            "constraints": [
                "Use a fixed SATB voicing; bass in root position.",
                "Minimize total voice-leading distance across all transitions.",
                "Each transition must be A₂-safe.",
                "No parallel fifths or octaves.",
            ],
            "solution": {
                "voicings": {
                    "C": ["E4", "C4", "G3", "C3"],
                    "Am": ["E4", "C4", "A3", "A2"],
                    "F": ["F4", "C4", "A3", "F3"],
                    "G": ["D4", "B3", "G3", "G3"],
                },
                "explanation": "Minimal motion; C→Am shares two common tones.",
            },
            "rubric": {"minimal_distance": 30, "no_parallels": 20, "a2_safe": 25, "voice_crossings": 25},
        },
        {
            "instructions": (
                "Identify the voice-leading distance between each pair of major triads in the "
                "keys C, D, E, F, G, A, B♭. Use the Eisenstein lattice to compute the distance "
                "as the sum of norm_sq() for each voice's pitch-class vector movement. "
                "Which pair has the smallest distance?"
            ),
            "starting_notes": [
                {"voice": "reference", "triads": ["C", "D", "E", "F", "G", "A", "B♭"]},
            ],
            "constraints": [
                "Use pitch-class vectors (mod 12) for each triad.",
                "Compute voice-leading distance using A₂ norm_sq().",
                "Find the minimum-distance pair.",
                "Present results as a distance matrix.",
            ],
            "solution": {
                "min_pair": ("C", "E"),
                "min_distance": 1.0,
                "explanation": "C major and E major share a common tone (E); total A₂ distance is minimal.",
            },
            "rubric": {"distance_computation": 35, "matrix_completeness": 25, "min_identification": 25, "a2_usage": 15},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="voice_leading", difficulty="beginner", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _voice_leading_intermediate(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Realize a four-part Bach-style chorale phrase (8 chords) with optimal voice leading. "
                "Model the voice-leading constraint graph as a Laman graph: for n=4 voices, verify "
                "2n-3=5 independent edges exist using henneberg_construct(). Each chord transition "
                "must preserve holonomic consistency."
            ),
            "starting_notes": [
                {"voice": "soprano", "pitches": ["G4", "A4", "B4", "C5", "D5", "C5", "B4", "A4", "G4"]},
                {"voice": "bass", "pitches": ["G2", "C3", "D3", "C3", "G2", "A2", "D3", "D3", "G2"]},
            ],
            "constraints": [
                "Fill in alto and tenor with smooth voice leading.",
                "Laman rigidity on the 4-voice constraint graph (5 independent edges).",
                "Holonomy consistency around all cycles of the voice graph.",
                "No parallel/displaced fifths or octaves.",
                "Resolve all dissonances (if any) by step.",
            ],
            "solution": {
                "alto": ["B3", "C4", "D4", "E4", "D4", "E4", "D4", "F4", "D4"],
                "tenor": ["D3", "E3", "F3", "G3", "B3", "A3", "F3", "F3", "G3"],
                "laman_edges": 5,
                "explanation": "SATB realization with Laman-rigid voice-leading graph.",
            },
            "rubric": {"voice_leading_smoothness": 25, "laman_rigidity": 25, "holonomy": 25, "style": 25},
        },
        {
            "instructions": (
                "Construct a neo-Riemannian PLR chain (P, L, R transformations) connecting "
                "C major to C♯ major in ≤ 6 moves. Each transformation shifts one voice by "
                "semitone. Verify that each single-voice shift snaps to an A₂ lattice point. "
                "Compute the total holonomy around the full transformation cycle."
            ),
            "starting_notes": [
                {"voice": "start", "triad": "C major", "pitches": ["C4", "E4", "G4"]},
                {"voice": "target", "triad": "C♯ major", "pitches": ["C♯4", "E♯4", "G♯4"]},
            ],
            "constraints": [
                "Use only Parallel (P), Leading-tone (L), and Relative (R) transformations.",
                "Each step moves exactly one voice by ±1 semitone.",
                "Verify A₂ snap safety for each voice movement.",
                "Compute holonomy_product() around the full chain.",
            ],
            "solution": {
                "chain": ["C", "Cm", "C♯m", "C♯"],
                "moves": ["P", "L", "P"],
                "total_steps": 3,
                "explanation": "C→P→Cm→L→C♯m→P→C♯ in 3 transformations, 3 semitones total.",
            },
            "rubric": {"plr_correctness": 30, "minimality": 25, "a2_snap": 25, "holonomy": 20},
        },
        {
            "instructions": (
                "Given a 12-tone row (C, D♭, E, F, G, A, B♭, B, D, E♭, G♭, A♭), find the "
                "voice-leading distance between the prime form and its inversion (retrograde-"
                "inverted). Use the Eisenstein A₂ lattice to compute pairwise distances between "
                "corresponding pitch-class vectors. Verify that the total displacement forms a "
                "Laman-rigid configuration when the 12 pitch classes are treated as nodes."
            ),
            "starting_notes": [
                {"voice": "prime_row", "pitches": ["C", "D♭", "E", "F", "G", "A", "B♭", "B", "D", "E♭", "G♭", "A♭"]},
            ],
            "constraints": [
                "Compute the retrograde-inversion of the row.",
                "Calculate A₂ voice-leading distance between prime and RI form.",
                "Model 12 pitch-class pairs as nodes; check Laman rigidity (2·12-3 = 21 edges).",
                "Report which pitch-class pair has the largest A₂ displacement.",
            ],
            "solution": {
                "ri_form": ["D", "A", "E", "C♯", "B", "A♭", "G", "F", "E♭", "C", "B♭", "G♭"],
                "total_distance": 48.0,
                "max_displacement_pair": (5, 8),
                "explanation": "Retrograde-inversion computed; Laman graph has 21 edges for 12 nodes.",
            },
            "rubric": {"ri_correctness": 25, "distance_computation": 25, "laman_check": 25, "max_displacement": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="voice_leading", difficulty="intermediate", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _voice_leading_advanced(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Design an optimal voice-leading network for all 24 major/minor triads using "
                "neo-Riemannian transformations. Build a graph where each edge weight is the "
                "A₂ voice-leading distance. Verify the graph is Laman-rigid in each local "
                "neighbourhood. Compute algebraic_connectivity() of the full graph and report "
                "which triads form the most weakly-connected pair."
            ),
            "starting_notes": [
                {"voice": "all_triads", "count": 24},
            ],
            "constraints": [
                "Build a 24-node graph with PLR edges weighted by A₂ distance.",
                "Each local 3-node neighbourhood must be Laman-rigid.",
                "Compute algebraic connectivity of the full graph.",
                "Identify the weakest edge (largest distance).",
            ],
            "solution": {
                "graph_nodes": 24,
                "plr_edges": 72,
                "algebraic_connectivity": 0.33,
                "weakest_edge": ("C♯", "F♯"),
                "explanation": "Full PLR network with A₂ weights; Laman-rigid locally.",
            },
            "rubric": {"graph_construction": 25, "local_laman": 25, "algebraic_connectivity": 25, "analysis": 25},
        },
        {
            "instructions": (
                "Construct a 4-voice homophonic passage of 12 chords where voice-leading "
                "smoothness is globally optimized. Model the passage as a temporal funnel: "
                "use TemporalAgent with deadband funnels to ensure each voice converges to "
                "its target within FunnelPhase.LOCKED. Verify the Henneberg construction "
                "of the inter-voice constraint graph produces a Laman-rigid structure."
            ),
            "starting_notes": [
                {"voice": "soprano", "pitches": ["C5", "D5", "E5", "F5", "G5", "A5", "G5", "F5", "E5", "D5", "C5"]},
                {"voice": "bass", "pitches": ["C3", "G2", "A2", "F2", "G2", "F2", "E2", "F2", "G2", "G2", "C3"]},
            ],
            "constraints": [
                "Fill alto and tenor; minimize total voice-leading distance.",
                "Each voice follows a temporal funnel: TIGHTENING → LOCKED within 3 chords.",
                "Full inter-voice graph must be Laman (5 independent edges).",
                "Holonomy consistency verified for all fundamental cycles.",
            ],
            "solution": {
                "alto": ["E4", "F4", "G4", "A4", "B4", "C5", "B4", "A4", "G4", "F4", "E4"],
                "tenor": ["G3", "B3", "C4", "C4", "D4", "A3", "G3", "A3", "B3", "B3", "G3"],
                "funnel_phases": "All voices reach LOCKED by chord 4.",
                "explanation": "Globally smooth voice leading with temporal funnel convergence.",
            },
            "rubric": {"global_optimality": 25, "funnel_convergence": 25, "laman_rigidity": 25, "holonomy": 25},
        },
        {
            "instructions": (
                "Analyze Scriabin's 'mystic chord' (C, F♯, B♭, E, A, D) as a pitch-class set. "
                "Find the minimal voice-leading path to the French augmented sixth chord (C, E♭, "
                "F♯, A♭) using A₂ lattice distances. Model both chords as nodes in a constraint "
                "graph and verify Laman rigidity of the combined system. Compute the holonomy "
                "product around the transition cycle."
            ),
            "starting_notes": [
                {"voice": "mystic", "pitches": ["C", "F♯", "B♭", "E", "A", "D"]},
                {"voice": "fr+6", "pitches": ["C", "E♭", "F♯", "A♭"]},
            ],
            "constraints": [
                "Map both chords to pitch-class vectors.",
                "Find minimal A₂-distance voice leading between them.",
                "Build combined constraint graph (6+4=10 pitch classes); verify Laman.",
                "Compute holonomy_product() around the transition.",
            ],
            "solution": {
                "minimal_vl": {"C→C": 0, "F♯→F♯": 0, "B♭→A♭": 2, "E→E♭": 1, "A→unused": None, "D→unused": None},
                "total_distance": 3,
                "explanation": "Two common tones preserved; 3 semitones total movement.",
            },
            "rubric": {"pitch_class_mapping": 20, "minimal_vl": 30, "laman_combined": 25, "holonomy": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="voice_leading", difficulty="advanced", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _harmonic_constraints_beginner(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Identify which of the following chord progressions satisfy the basic harmonic "
                "constraint: each chord must share at least one pitch class with its neighbour "
                "(maximal smoothness). Map each chord's pitch classes onto the A₂ lattice and "
                "verify that shared tones snap to identical lattice points."
            ),
            "starting_notes": [
                {"voice": "progressions", "sequences": [
                    ["C", "Am", "F", "G"],
                    ["C", "E", "Am", "F"],
                    ["C", "Dm", "G7", "C"],
                    ["C", "A♭", "B♭", "Cm"],
                ]},
            ],
            "constraints": [
                "Each adjacent pair must share ≥ 1 pitch class.",
                "Shared tones must map to identical A₂ lattice points.",
                "Identify which progressions pass and which fail.",
                "For failures, identify the 'gap' (distance between nearest pitch classes).",
            ],
            "solution": {
                "pass": [["C", "Am", "F", "G"], ["C", "Dm", "G7", "C"]],
                "fail": [["C", "E", "Am", "F"], ["C", "A♭", "B♭", "Cm"]],
                "explanation": "Progressions 1 and 3 share common tones; 2 and 4 have gaps.",
            },
            "rubric": {"classification": 30, "a2_verification": 25, "gap_analysis": 25, "explanation": 20},
        },
        {
            "instructions": (
                "Build a harmonic constraint graph for the key of C major. Nodes are the 7 "
                "diatonic triads (I, ii, iii, IV, V, vi, vii°). Edges connect triads that "
                "share ≥ 1 pitch class. Compute the degree of each node and verify the graph "
                "is connected. Map shared pitch classes to A₂ lattice points."
            ),
            "starting_notes": [
                {"voice": "key", "tonic": "C", "triads": ["I", "ii", "iii", "IV", "V", "vi", "vii°"]},
            ],
            "constraints": [
                "Edge exists iff two triads share ≥ 1 pitch class.",
                "Verify graph connectivity (all nodes reachable from I).",
                "Map shared pitch classes to A₂ lattice coordinates.",
                "Report degree of each node.",
            ],
            "solution": {
                "degrees": {"I": 4, "ii": 3, "iii": 3, "IV": 4, "V": 3, "vi": 4, "vii°": 4},
                "connected": True,
                "explanation": "All diatonic triads connected; each shares tones with 3-4 others.",
            },
            "rubric": {"graph_construction": 30, "connectivity": 20, "a2_mapping": 25, "degree_report": 25},
        },
        {
            "instructions": (
                "Given the chord progression C → G → Am → F → C, identify all harmonic "
                "constraints being satisfied (voice-leading distance, common-tone preservation, "
                "functional harmony). For each transition, compute the A₂ voice-leading distance "
                "and classify it as 'smooth' (distance ≤ 3) or 'rough' (distance > 3)."
            ),
            "starting_notes": [
                {"voice": "progression", "chords": ["C major", "G major", "A minor", "F major", "C major"]},
            ],
            "constraints": [
                "Compute A₂ distance for each chord transition.",
                "Classify each transition as smooth or rough.",
                "Count total common tones across the full progression.",
                "Identify the smoothest transition.",
            ],
            "solution": {
                "distances": [4, 2, 2, 4],
                "classifications": ["rough", "smooth", "smooth", "rough"],
                "smoothest": "G→Am (distance 2)",
                "explanation": "G→Am and Am→F are smoothest; C→G and F→C are rougher.",
            },
            "rubric": {"distance_computation": 30, "classification": 25, "common_tones": 20, "smoothest_id": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="harmonic_constraints", difficulty="beginner", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _harmonic_constraints_intermediate(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Construct a Laman-rigid harmonic constraint graph for a 16-bar chord progression "
                "in C major. The graph must have exactly 2n-3 edges where n is the number of "
                "distinct chords. Use henneberg_construct() to build the graph incrementally. "
                "Verify each edge represents a valid voice-leading constraint (common tone or "
                "smooth voice leading ≤ 3 semitones total)."
            ),
            "starting_notes": [
                {"voice": "key", "tonic": "C", "bars": 16},
            ],
            "constraints": [
                "Select 6-8 distinct chords for the progression.",
                "Build Laman graph with 2n-3 edges via Henneberg construction.",
                "Each edge: voice-leading distance ≤ 3 semitones.",
                "Verify algebraic_connectivity() > 0 (connected graph).",
            ],
            "solution": {
                "chords": ["C", "Am", "F", "G", "Dm", "Em", "C"],
                "laman_edges": 11,
                "algebraic_connectivity": 0.45,
                "explanation": "7 chords, 11 edges = 2·7-3; all transitions smooth.",
            },
            "rubric": {"progression_quality": 20, "laman_construction": 30, "edge_validity": 25, "connectivity": 25},
        },
        {
            "instructions": (
                "Analyze the harmonic function of each chord in a modulation from C major to "
                "G major and back. Model the tonal regions as separate constraint sub-graphs "
                "connected by a 'pivot chord'. Verify holonomic consistency within each region "
                "and across the modulation boundary using verify_consistency()."
            ),
            "starting_notes": [
                {"voice": "progression", "chords": ["C", "Am", "D7", "G", "Em", "C", "D7", "G", "Am", "C"]},
            ],
            "constraints": [
                "Identify the pivot chord(s) for the modulation.",
                "Build sub-graph for each tonal region.",
                "Verify holonomic consistency in each region.",
                "Verify consistency across the modulation boundary.",
            ],
            "solution": {
                "pivot": "Am (vi in C, ii in G)",
                "c_region_holonomy": True,
                "g_region_holonomy": True,
                "boundary_consistent": True,
                "explanation": "Am serves as pivot; both regions holonomically consistent.",
            },
            "rubric": {"pivot_identification": 25, "subgraph_construction": 25, "holonomy_per_region": 25, "boundary": 25},
        },
        {
            "instructions": (
                "Build a harmonic lattice where each node is a chord quality (major, minor, "
                "diminished, augmented, dominant 7th) and edges represent single-semitone "
                "voice-leading transformations. Compute the A₂ distance for each edge. "
                "Verify the lattice is Laman-rigid for each local 3-node triangle. "
                "Identify the most 'central' chord quality (highest degree)."
            ),
            "starting_notes": [
                {"voice": "qualities", "types": ["major", "minor", "diminished", "augmented", "dom7"]},
            ],
            "constraints": [
                "Edge exists iff single-semitone voice leading connects the chord qualities.",
                "Compute A₂ distance for each edge.",
                "Verify Laman rigidity for each triangular face.",
                "Find the most central node (highest degree).",
            ],
            "solution": {
                "most_central": "dom7 (connects to all others via semitone shifts)",
                "edge_count": 8,
                "laman_triangles_pass": True,
                "explanation": "Dom7 is maximally connected; all local triangles are Laman-rigid.",
            },
            "rubric": {"lattice_construction": 25, "a2_distances": 25, "laman_verification": 25, "centrality": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="harmonic_constraints", difficulty="intermediate", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _harmonic_constraints_advanced(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Design a generative harmonic grammar as a Laman-rigid constraint system. The "
                "grammar must: (1) produce only syntactically valid progressions, (2) enforce "
                "voice-leading smoothness (A₂ distance ≤ 2 per transition), (3) guarantee "
                "holonomic consistency across all generated paths. Implement as a Henneberg "
                "construction where each added chord introduces exactly 2 new constraints. "
                "Verify with algebraic_connectivity() and verify_consistency()."
            ),
            "starting_notes": [
                {"voice": "grammar", "rules": "design from scratch"},
            ],
            "constraints": [
                "Laman-rigid: 2n-3 constraints for n chords.",
                "Voice-leading smoothness: A₂ distance ≤ 2.",
                "Holonomic consistency on all cycles.",
                "algebraic_connectivity() must be > 0.",
            ],
            "solution": {
                "grammar": {
                    "start": "I",
                    "rules": {"I": ["IV", "V", "vi"], "IV": ["V", "I"], "V": ["I", "vi"], "vi": ["ii", "IV"]},
                },
                "laman_verified": True,
                "holonomy_verified": True,
                "explanation": "Grammar generates valid progressions with guaranteed smoothness.",
            },
            "rubric": {"grammar_validity": 25, "laman_rigidity": 25, "smoothness_guarantee": 25, "holonomy": 25},
        },
        {
            "instructions": (
                "Analyze the complete harmonic structure of a Bach chorale phrase as a constraint "
                "satisfaction problem. Each chord is a variable; voice-leading constraints between "
                "adjacent chords are binary constraints. Build the full CSP, verify Laman rigidity "
                "of the constraint graph, and solve for the unique voice-leading realization using "
                "holonomy verification. Compare with Bach's original."
            ),
            "starting_notes": [
                {"voice": "bach", "phrase": "BWV 1, phrase 1", "chords": 8},
            ],
            "constraints": [
                "Model each chord as a CSP variable with domain = all valid SATB voicings.",
                "Binary constraints: voice leading distance, no parallels, A₂ safety.",
                "Constraint graph must be Laman-rigid (2n-3 edges for n chords).",
                "Holonomy verification on all fundamental cycles.",
            ],
            "solution": {
                "csp_solved": True,
                "unique_solution": False,
                "solutions_count": 3,
                "bach_matches_rank": 1,
                "explanation": "CSP yields 3 valid realizations; Bach's is the optimal one.",
            },
            "rubric": {"csp_formulation": 25, "laman_rigidity": 25, "solution_quality": 25, "bach_comparison": 25},
        },
        {
            "instructions": (
                "Build a cross-tonal harmonic constraint system that simultaneously models "
                "progressions in two related keys (C major and A minor). The system must "
                "maintain independent Laman-rigid constraint graphs for each tonal region "
                "while ensuring holonomic consistency at all pivot points. Use "
                "henneberg_construct() for each region and verify_consistency() for cross-"
                "regional cycles."
            ),
            "starting_notes": [
                {"voice": "dual_tonal", "keys": ["C major", "A minor"], "shared_chords": ["C", "Am", "F", "G", "Em"]},
            ],
            "constraints": [
                "Build Laman graph for C-major region (n₁ chords, 2n₁-3 edges).",
                "Build Laman graph for A-minor region (n₂ chords, 2n₂-3 edges).",
                "Pivot chords must satisfy both regional constraints.",
                "Cross-regional holonomy must be verified on all boundary cycles.",
            ],
            "solution": {
                "c_region": {"chords": 5, "laman_edges": 7},
                "am_region": {"chords": 5, "laman_edges": 7},
                "pivots": ["C", "Am", "F"],
                "cross_holonomy_pass": True,
                "explanation": "Both regions independently Laman-rigid; pivots consistent across regions.",
            },
            "rubric": {"regional_laman": 25, "pivot_consistency": 25, "cross_holonomy": 25, "completeness": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="harmonic_constraints", difficulty="advanced", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _rhythmic_constraints_beginner(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Construct a 4-measure rhythmic pattern in 4/4 time using only quarter and half "
                "notes. Model the pattern as a temporal constraint: each note onset must align "
                "with a metronome tick. Use the Metronome class to generate ticks at ♩=120 and "
                "verify every onset falls on a tick."
            ),
            "starting_notes": [
                {"voice": "rhythm", "time_sig": "4/4", "tempo": 120, "measures": 4},
            ],
            "constraints": [
                "Use only quarter (♩) and half (𝅗𝅥) notes.",
                "Every onset must coincide with a Metronome tick.",
                "Total duration per measure = 4 beats exactly.",
                "Include at least one half note per measure.",
            ],
            "solution": {
                "pattern": ["♩", "♩", "𝅗𝅥", "♩", "♩", "𝅗𝅥", "𝅗𝅥", "𝅗𝅥", "♩", "♩", "♩", "♩"],
                "onsets_verified": True,
                "explanation": "All onsets align with metronome ticks at 120 BPM.",
            },
            "rubric": {"note_values": 25, "metronome_alignment": 30, "measure_completeness": 20, "variety": 25},
        },
        {
            "instructions": (
                "Create a two-voice rhythmic duet in 3/4 time (4 measures). Voice 1 uses "
                "quarter notes; Voice 2 uses dotted half notes. Verify the rhythmic alignment "
                "using Metronome ticks. Model the inter-voice timing as a temporal constraint: "
                "Voice 2's onsets must be a subset of Voice 1's onsets."
            ),
            "starting_notes": [
                {"voice": "voice_1", "time_sig": "3/4", "values": "quarter"},
                {"voice": "voice_2", "time_sig": "3/4", "values": "dotted_half"},
            ],
            "constraints": [
                "Voice 1: 3 quarter notes per measure.",
                "Voice 2: 1 dotted half note per measure.",
                "Voice 2 onsets ⊂ Voice 1 onsets (every bar line).",
                "Verify with Metronome at ♩=100.",
            ],
            "solution": {
                "voice_1": ["♩", "♩", "♩"] * 4,
                "voice_2": ["𝅝."] * 4,
                "subset_verified": True,
                "explanation": "Dotted half onsets (bar lines) are a subset of quarter-note onsets.",
            },
            "rubric": {"voice_1_correctness": 25, "voice_2_correctness": 25, "subset_verification": 25, "metronome_check": 25},
        },
        {
            "instructions": (
                "Generate a simple 8-beat rhythm using eighth and quarter notes. Verify that "
                "the total duration sums to exactly 8 beats and that each onset snaps to a "
                "Metronome tick. Introduce a temporal funnel: the rhythm starts imprecise "
                "(±0.1 beat tolerance) and tightens to exact (±0.0) by beat 8."
            ),
            "starting_notes": [
                {"voice": "rhythm", "total_beats": 8},
            ],
            "constraints": [
                "Use only eighth (♪) and quarter (♩) notes.",
                "Total duration = 8 beats.",
                "Each onset aligned to Metronome tick.",
                "Temporal funnel: tolerance decreases from 0.1 to 0.0 over 8 beats.",
            ],
            "solution": {
                "pattern": ["♪", "♪", "♩", "♪", "♪", "♩", "♩", "♩"],
                "duration_check": 8.0,
                "funnel_converged": True,
                "explanation": "Tolerance decreases linearly; exact alignment at beat 8.",
            },
            "rubric": {"duration_accuracy": 25, "metronome_alignment": 25, "funnel_convergence": 25, "note_values": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="rhythmic_constraints", difficulty="beginner", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _rhythmic_constraints_intermediate(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Compose a polymetric exercise: Voice 1 in 4/4, Voice 2 in 3/4, both at "
                "♩=90. Find the least common multiple (LCM) of bar lengths where both voices "
                "align. Model as two Metronome instances; verify alignment at the LCM boundary "
                "using a deadband temporal funnel. Both voices must converge to LOCKED phase "
                "at the alignment point."
            ),
            "starting_notes": [
                {"voice": "voice_1", "time_sig": "4/4", "tempo": 90},
                {"voice": "voice_2", "time_sig": "3/4", "tempo": 90},
            ],
            "constraints": [
                "Voice 1: 4/4 pattern repeated.",
                "Voice 2: 3/4 pattern repeated.",
                "LCM alignment at 12 beats (3 bars of 4/4 = 4 bars of 3/4).",
                "Temporal funnel converges to LOCKED at beat 12.",
            ],
            "solution": {
                "lcm_beats": 12,
                "voice_1_bars": 3,
                "voice_2_bars": 4,
                "funnel_phase_at_alignment": "LOCKED",
                "explanation": "LCM(4,3)=12; both voices align with LOCKED funnel convergence.",
            },
            "rubric": {"lcm_correctness": 25, "metronome_sync": 25, "funnel_convergence": 25, "pattern_quality": 25},
        },
        {
            "instructions": (
                "Build a syncopated 8-bar rhythm in 4/4 where strong-beat onsets are delayed "
                "by one eighth note. Model the displacement as a temporal constraint: the "
                "Metronome provides reference ticks, and the actual onsets must fall within "
                "a deadband funnel of ±0.25 beats around the displaced tick. Verify the "
                "funnel tightens from TIGHTENING to LOCKED over the 8 bars."
            ),
            "starting_notes": [
                {"voice": "rhythm", "time_sig": "4/4", "measures": 8, "displacement": "eighth"},
            ],
            "constraints": [
                "All originally strong-beat positions displaced by +1 eighth note.",
                "Onsets within deadband funnel of ±0.25 around displaced ticks.",
                "Funnel must reach LOCKED by bar 6.",
                "Total duration per bar = 4 beats.",
            ],
            "solution": {
                "displaced_onsets": "All strong beats shifted by 0.5 beats.",
                "funnel_locked_by": "bar 6",
                "deadband_satisfied": True,
                "explanation": "Syncopation pattern with tightening funnel converging to exact displacement.",
            },
            "rubric": {"displacement_accuracy": 25, "funnel_phases": 25, "deadband_compliance": 25, "bar_completeness": 25},
        },
        {
            "instructions": (
                "Design a 3-voice hocket where each voice sounds on non-overlapping subdivisions "
                "of the beat. Voice 1: beats 1, 4, 7, 10; Voice 2: beats 2, 5, 8, 11; "
                "Voice 3: beats 3, 6, 9, 12. Verify using three synchronized Metronome instances "
                "that no two voices sound simultaneously. Model the constraint as Laman rigidity: "
                "3 voices require 2·3-3=3 independent anti-coincidence constraints."
            ),
            "starting_notes": [
                {"voice": "voice_1", "beats": [1, 4, 7, 10]},
                {"voice": "voice_2", "beats": [2, 5, 8, 11]},
                {"voice": "voice_3", "beats": [3, 6, 9, 12]},
            ],
            "constraints": [
                "No two voices may have simultaneous onsets.",
                "Each onset aligned to Metronome tick.",
                "Laman constraint: 3 anti-coincidence edges between 3 voices.",
                "Every beat position 1-12 must be covered by exactly one voice.",
            ],
            "solution": {
                "coverage": "complete (beats 1-12 each assigned to exactly one voice)",
                "no_coincidence": True,
                "laman_edges": 3,
                "explanation": "Perfect hocket; all beats covered, zero overlaps.",
            },
            "rubric": {"no_overlap": 30, "complete_coverage": 25, "metronome_sync": 20, "laman_constraint": 25},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="rhythmic_constraints", difficulty="intermediate", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


def _rhythmic_constraints_advanced(rng: random.Random) -> Exercise:
    templates = [
        {
            "instructions": (
                "Design a fully distributed metronome consensus system for a 5-piece ensemble. "
                "Each musician runs an independent Metronome instance with slight tempo drift "
                "(±0.5 BPM). Use the metronome consensus algorithm to synchronize all 5 instances "
                "within a deadband funnel. Verify convergence to LOCKED phase within 8 cycles. "
                "Model the inter-musician coupling as a Laman graph (2·5-3=7 edges) and verify "
                "algebraic_connectivity() > 0."
            ),
            "starting_notes": [
                {"voice": "ensemble", "musicians": 5, "nominal_tempo": 120, "drift": "±0.5 BPM"},
            ],
            "constraints": [
                "5 Metronome instances with ±0.5 BPM drift.",
                "Laman-rigid coupling graph: 7 independent edges.",
                "Convergence to LOCKED within 8 consensus cycles.",
                "algebraic_connectivity() > 0 on the coupling graph.",
            ],
            "solution": {
                "convergence_cycles": 6,
                "final_phase": "LOCKED",
                "laman_edges": 7,
                "algebraic_connectivity": 0.52,
                "explanation": "Full consensus in 6 cycles with Laman-rigid coupling.",
            },
            "rubric": {"consensus_convergence": 25, "laman_coupling": 25, "funnel_phases": 25, "algebraic_connectivity": 25},
        },
        {
            "instructions": (
                "Construct a Euclidean rhythm (Björklund's algorithm) for n=13 onsets in k=8 "
                "pulses. Verify the resulting pattern has maximal evenness by computing the "
                "A₂ distance between onset positions and the ideal evenly-spaced grid. Build "
                "a Metronome-driven temporal funnel that starts at TIGHTENING and locks to "
                "the Euclidean pattern by the end of one full cycle."
            ),
            "starting_notes": [
                {"voice": "rhythm", "pulses": 8, "onsets": 5},
            ],
            "constraints": [
                "Generate Euclidean rhythm E(5, 8).",
                "Compute A₂ distance between actual and ideal onset positions.",
                "Temporal funnel: TIGHTENING → LOCKED over one cycle.",
                "Verify maximal evenness (no consecutive gap difference > 1).",
            ],
            "solution": {
                "euclidean_pattern": [1, 0, 1, 0, 1, 0, 1, 1],
                "max_evenness": True,
                "funnel_locked": True,
                "explanation": "E(5,8) = [10010101]; maximal evenness verified.",
            },
            "rubric": {"euclidean_correctness": 30, "evenness_verification": 25, "funnel_convergence": 25, "a2_distance": 20},
        },
        {
            "instructions": (
                "Design a multi-layered rhythmic constraint system for a 4-voice piece with "
                "independent tempo layers (♩=60, ♩=80, ♩=100, ♩=120). Each layer has its own "
                "Metronome. Build a cross-layer consensus mechanism that brings all layers into "
                "phase alignment at the LCM of their beat periods. The consensus graph must be "
                "Laman-rigid (2·4-3=5 edges). Verify holonomic consistency across all cross-layer "
                "cycles. Use temporal funnels with phase-specific deadband widths."
            ),
            "starting_notes": [
                {"voice": "layer_1", "tempo": 60},
                {"voice": "layer_2", "tempo": 80},
                {"voice": "layer_3", "tempo": 100},
                {"voice": "layer_4", "tempo": 120},
            ],
            "constraints": [
                "4 independent tempo layers with separate Metronome instances.",
                "LCM alignment point computed and verified.",
                "Laman-rigid consensus graph: 5 independent coupling edges.",
                "Holonomy consistency on all cross-layer cycles.",
                "Temporal funnel convergence at LCM boundary.",
            ],
            "solution": {
                "lcm_beats": 1200,
                "alignment_time_seconds": 60.0,
                "laman_edges": 5,
                "holonomy_pass": True,
                "explanation": "All layers align at 60s; Laman-rigid coupling ensures robust consensus.",
            },
            "rubric": {"lcm_computation": 20, "laman_rigidity": 20, "holonomy": 20, "funnel_convergence": 20, "cross_layer_consensus": 20},
        },
    ]
    t = _pick(rng, templates)
    return Exercise(topic="rhythmic_constraints", difficulty="advanced", seed=None,
                    instructions=t["instructions"], starting_notes=t["starting_notes"],
                    constraints=t["constraints"], solution=t["solution"],
                    scoring_rubric=t["rubric"])


# ---------------------------------------------------------------------------
# Topic × Difficulty dispatch table
# ---------------------------------------------------------------------------

_DISPATCH = {
    ("species_counterpoint", "beginner"): _species_counterpoint_beginner,
    ("species_counterpoint", "intermediate"): _species_counterpoint_intermediate,
    ("species_counterpoint", "advanced"): _species_counterpoint_advanced,
    ("voice_leading", "beginner"): _voice_leading_beginner,
    ("voice_leading", "intermediate"): _voice_leading_intermediate,
    ("voice_leading", "advanced"): _voice_leading_advanced,
    ("harmonic_constraints", "beginner"): _harmonic_constraints_beginner,
    ("harmonic_constraints", "intermediate"): _harmonic_constraints_intermediate,
    ("harmonic_constraints", "advanced"): _harmonic_constraints_advanced,
    ("rhythmic_constraints", "beginner"): _rhythmic_constraints_beginner,
    ("rhythmic_constraints", "intermediate"): _rhythmic_constraints_intermediate,
    ("rhythmic_constraints", "advanced"): _rhythmic_constraints_advanced,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_exercise(
    topic: str,
    difficulty: str,
    seed: int | None = None,
) -> dict[str, Any]:
    """Generate a constrained-composition exercise.

    Parameters
    ----------
    topic : str
        One of "species_counterpoint", "voice_leading",
        "harmonic_constraints", "rhythmic_constraints".
    difficulty : str
        One of "beginner", "intermediate", "advanced".
    seed : int | None
        Random seed for reproducibility.  Pass the same seed to get the
        same exercise template every time.

    Returns
    -------
    dict
        Exercise dictionary with keys: topic, difficulty, instructions,
        starting_notes, constraints, solution, scoring_rubric, seed.

    Raises
    ------
    ValueError
        If *topic* or *difficulty* is not recognised.
    """
    if topic not in TOPICS:
        raise ValueError(f"Unknown topic {topic!r}. Choose from {TOPICS}")
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Unknown difficulty {difficulty!r}. Choose from {DIFFICULTIES}")

    rng = random.Random(seed)
    builder = _DISPATCH[(topic, difficulty)]
    exercise = builder(rng)
    exercise.seed = seed
    return exercise.to_dict()


# ---------------------------------------------------------------------------
# CLI support  (python -m constraint_theory_core exercise ...)
# ---------------------------------------------------------------------------

def _cli_exercise(args) -> None:
    """Handle the ``exercise`` CLI sub-command."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="constraint_theory_core exercise",
        description="Generate a constrained-composition exercise.",
    )
    parser.add_argument("--topic", required=True, choices=TOPICS,
                        help="Exercise topic")
    parser.add_argument("--difficulty", required=True, choices=DIFFICULTIES,
                        help="Difficulty level")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--show-solution", action="store_true",
                        help="Include the solution in output")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output as JSON")
    parsed = parser.parse_args(args)

    ex = generate_exercise(parsed.topic, parsed.difficulty, seed=parsed.seed)

    if not parsed.show_solution:
        ex["solution"] = "(hidden — use --show-solution to reveal)"

    if parsed.as_json:
        print(json.dumps(ex, indent=2))
    else:
        print(f"Topic:       {ex['topic']}")
        print(f"Difficulty:  {ex['difficulty']}")
        print(f"Seed:        {ex['seed']}")
        print()
        print("Instructions:")
        print(f"  {ex['instructions']}")
        print()
        print("Starting Notes:")
        for note_set in ex["starting_notes"]:
            print(f"  {note_set}")
        print()
        print("Constraints:")
        for c in ex["constraints"]:
            print(f"  • {c}")
        print()
        if isinstance(ex["solution"], dict):
            print("Solution:")
            print(json.dumps(ex["solution"], indent=2))
        else:
            print(f"Solution: {ex['solution']}")
        print()
        print("Scoring Rubric:")
        total = sum(ex["scoring_rubric"].values())
        for criterion, pts in ex["scoring_rubric"].items():
            print(f"  {criterion}: {pts}/{total}")
