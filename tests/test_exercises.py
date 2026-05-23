"""Tests for constraint_theory_core.exercises."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from constraint_theory_core.exercises import (
    DIFFICULTIES,
    TOPICS,
    generate_exercise,
)


# ---------------------------------------------------------------------------
# Parameterised smoke test — every (topic, difficulty) pair
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_generate_exercise_returns_valid_dict(topic, difficulty):
    ex = generate_exercise(topic, difficulty, seed=42)

    # Required keys
    for key in (
        "topic", "difficulty", "instructions", "starting_notes",
        "constraints", "solution", "scoring_rubric", "seed",
    ):
        assert key in ex, f"Missing key: {key!r}"

    assert ex["topic"] == topic
    assert ex["difficulty"] == difficulty
    assert ex["seed"] == 42
    assert isinstance(ex["instructions"], str)
    assert len(ex["instructions"]) > 20
    assert isinstance(ex["starting_notes"], list)
    assert len(ex["starting_notes"]) > 0
    assert isinstance(ex["constraints"], list)
    assert len(ex["constraints"]) >= 2
    assert isinstance(ex["solution"], dict)
    assert isinstance(ex["scoring_rubric"], dict)
    assert sum(ex["scoring_rubric"].values()) > 0


# ---------------------------------------------------------------------------
# Reproducibility — same seed → same exercise
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_seed_reproducibility(topic, difficulty):
    a = generate_exercise(topic, difficulty, seed=123)
    b = generate_exercise(topic, difficulty, seed=123)
    assert a == b, "Same seed should produce identical exercises"


# ---------------------------------------------------------------------------
# Different seeds may produce different templates
# ---------------------------------------------------------------------------

def test_different_seeds_may_differ():
    # Not guaranteed for small template pools, but very likely
    exercises = [generate_exercise("species_counterpoint", "beginner", seed=i) for i in range(20)]
    instructions = {e["instructions"] for e in exercises}
    # With 3 templates and 20 seeds, P(all same) ≈ (1/3)^19 ≈ negligible
    assert len(instructions) > 1, "Expected at least 2 different templates across 20 seeds"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_invalid_topic_raises():
    with pytest.raises(ValueError, match="Unknown topic"):
        generate_exercise("nonexistent_topic", "beginner")


def test_invalid_difficulty_raises():
    with pytest.raises(ValueError, match="Unknown difficulty"):
        generate_exercise("species_counterpoint", "expert")


# ---------------------------------------------------------------------------
# Topic-specific structure checks
# ---------------------------------------------------------------------------

def test_species_counterpoint_has_pitch_data():
    ex = generate_exercise("species_counterpoint", "beginner", seed=0)
    # At least one starting_notes entry should have "pitches"
    has_pitches = any("pitches" in sn for sn in ex["starting_notes"])
    assert has_pitches


def test_voice_leading_has_voices():
    ex = generate_exercise("voice_leading", "intermediate", seed=0)
    assert len(ex["starting_notes"]) >= 1


def test_harmonic_has_progression_data():
    ex = generate_exercise("harmonic_constraints", "beginner", seed=0)
    # Should reference chords or triads in starting_notes or instructions
    text = str(ex["starting_notes"]) + ex["instructions"]
    assert "chord" in text.lower() or "triad" in text.lower()


def test_rhythmic_has_timing():
    ex = generate_exercise("rhythmic_constraints", "beginner", seed=0)
    text = str(ex["starting_notes"]) + ex["instructions"]
    assert "beat" in text.lower() or "tempo" in text.lower() or "measure" in text.lower()


# ---------------------------------------------------------------------------
# Rubric integrity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_rubric_sums_to_reasonable_total(topic, difficulty):
    ex = generate_exercise(topic, difficulty, seed=0)
    total = sum(ex["scoring_rubric"].values())
    assert total >= 60, f"Rubric total {total} seems too low"
    assert total <= 120, f"Rubric total {total} seems too high"


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

def test_cli_exercise_basic():
    result = subprocess.run(
        [sys.executable, "-m", "constraint_theory_core", "exercise",
         "--topic", "species_counterpoint", "--difficulty", "beginner", "--seed", "7"],
        capture_output=True, text=True, cwd=_repo_root(),
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Topic:" in result.stdout
    assert "species_counterpoint" in result.stdout
    assert "(hidden" in result.stdout


def test_cli_exercise_with_solution():
    result = subprocess.run(
        [sys.executable, "-m", "constraint_theory_core", "exercise",
         "--topic", "voice_leading", "--difficulty", "beginner",
         "--show-solution", "--seed", "1"],
        capture_output=True, text=True, cwd=_repo_root(),
    )
    assert result.returncode == 0
    assert "(hidden" not in result.stdout
    assert "Solution:" in result.stdout


def test_cli_exercise_json_output():
    result = subprocess.run(
        [sys.executable, "-m", "constraint_theory_core", "exercise",
         "--topic", "rhythmic_constraints", "--difficulty", "advanced",
         "--show-solution", "--json", "--seed", "42"],
        capture_output=True, text=True, cwd=_repo_root(),
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["topic"] == "rhythmic_constraints"
    assert data["difficulty"] == "advanced"


def test_cli_exercise_bad_topic():
    result = subprocess.run(
        [sys.executable, "-m", "constraint_theory_core", "exercise",
         "--topic", "nonexistent"],
        capture_output=True, text=True, cwd=_repo_root(),
    )
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# Template count check — at least 3 per (topic, difficulty)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_at_least_three_templates(topic, difficulty):
    """Verify the dispatch produces ≥3 distinct templates across seeds."""
    instructions = set()
    for seed in range(50):
        ex = generate_exercise(topic, difficulty, seed=seed)
        instructions.add(ex["instructions"])
    assert len(instructions) >= 3, (
        f"Expected ≥3 distinct templates for ({topic}, {difficulty}), got {len(instructions)}"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root():
    """Return the repository root (parent of this file's directory)."""
    import pathlib
    return str(pathlib.Path(__file__).resolve().parent.parent)
