//! Musical cohomology — simplicial cohomology on chord progressions.
//!
//! Models chord progressions as simplicial complexes and computes
//! H0 (connected components) and H1 (independent cycles / harmonic holes).

/// Result of cohomology computation.
#[derive(Debug, Clone, PartialEq)]
pub struct CohomologyResult {
    /// Number of connected components.
    pub h0: usize,
    /// Number of independent cycles (Betti number 1).
    pub h1: usize,
    /// Whether emergence (harmonic holes) was detected.
    pub emergence_detected: bool,
}

/// Compute simplicial cohomology on a chord progression.
///
/// - `chords`: chord root notes (vertices)
/// - `transitions`: pairs `(from, to)` as flat slice `[f0, t0, f1, t1, ...]`
///
/// Uses BFS for connected components and the cyclomatic number for H1.
pub fn musical_cohomology(chords: &[i32], transitions: &[i32]) -> CohomologyResult {
    let n = chords.len();
    if n == 0 {
        return CohomologyResult {
            h0: 0,
            h1: 0,
            emergence_detected: false,
        };
    }

    let n_trans = transitions.len() / 2;

    // Build adjacency list
    let mut adj: Vec<Vec<usize>> = vec![vec![]; n];
    let mut unique_edges = 0usize;

    for i in 0..n_trans {
        let from = transitions[i * 2] as usize;
        let to = transitions[i * 2 + 1] as usize;
        if from >= n || to >= n {
            continue;
        }

        // Add undirected edge (deduplicate)
        let (u, v) = (from.min(to), from.max(to));
        if !adj[u].contains(&v) {
            adj[u].push(v);
            adj[v].push(u);
            unique_edges += 1;
        }
    }

    // BFS for connected components
    let mut visited = vec![false; n];
    let mut h0 = 0usize;
    let mut queue = std::collections::VecDeque::new();

    for start in 0..n {
        if visited[start] {
            continue;
        }
        h0 += 1;
        queue.clear();
        queue.push_back(start);
        visited[start] = true;
        while let Some(u) = queue.pop_front() {
            for &v in &adj[u] {
                if !visited[v] {
                    visited[v] = true;
                    queue.push_back(v);
                }
            }
        }
    }

    // Cyclomatic number: H1 = edges - vertices + components
    let h1 = (unique_edges as i64 - n as i64 + h0 as i64).max(0) as usize;

    CohomologyResult {
        h0,
        h1,
        emergence_detected: h1 > 0,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_chord() {
        let result = musical_cohomology(&[0], &[]);
        assert_eq!(result.h0, 1);
        assert_eq!(result.h1, 0);
        assert!(!result.emergence_detected);
    }

    #[test]
    fn test_cycle_h1() {
        // 3 chords in a cycle → H1 = 1
        let result = musical_cohomology(&[0, 4, 7], &[0, 1, 1, 2, 2, 0]);
        assert_eq!(result.h0, 1);
        assert_eq!(result.h1, 1);
        assert!(result.emergence_detected);
    }

    #[test]
    fn test_disconnected() {
        let result = musical_cohomology(&[0, 1, 2, 3], &[0, 1, 2, 3]);
        assert_eq!(result.h0, 2);
    }

    #[test]
    fn test_no_transitions() {
        let result = musical_cohomology(&[0, 4, 7], &[]);
        assert_eq!(result.h0, 3);
        assert_eq!(result.h1, 0);
    }

    #[test]
    fn test_empty() {
        let result = musical_cohomology(&[], &[]);
        assert_eq!(result.h0, 0);
    }

    #[test]
    fn test_double_cycle() {
        // 4 chords: 0→1→2→0 and 0→3→0
        // Unique undirected edges: 0-1, 1-2, 0-2, 0-3 = 4 edges
        // H1 = 4 - 4 + 1 = 1
        let result = musical_cohomology(&[0, 4, 7, 11], &[0, 1, 1, 2, 2, 0, 0, 3, 3, 0]);
        assert_eq!(result.h0, 1);
        assert_eq!(result.h1, 1);
    }

    #[test]
    fn test_tree() {
        // Tree: 0→1, 0→2, 0→3 → no cycles, H1=0
        let result = musical_cohomology(&[0, 1, 2, 3], &[0, 1, 0, 2, 0, 3]);
        assert_eq!(result.h0, 1);
        assert_eq!(result.h1, 0);
    }
}
