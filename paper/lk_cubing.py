#!/usr/bin/env python3
"""
Exact analysis of Lower Kurast (LK) superchests under Fruit's (bonqen) reverse-engineered
drop model (d2pg) with clean-room vanilla verification by fearedbliss, incorporating
the locked vs. unlocked chest mechanics, Markov chain cubing to a target rune, and /players 5 vs /players 7.
"""

import math
import numpy as np

# Total 16-bit truncated seed patterns (Fruit's d2pg, verified by fearedbliss):
# 2^16 - 2 = 65,534 (or 65,536; we verify both and note the 0.003% difference)
TOTAL_PATTERNS = 65534

# In Hell Lower Kurast (alvl = 80), chest lock probability is 20% (or 19% in some guides;
# note that in the d2pg / d2runes weighted tables by TheHappyDev:
# https://d2runes.io/rune-farming/lk-farming
# 0.80 * unlocked + 0.20 * locked gives the exact .2 and .4 decimals!)
P_UNLOCKED = 0.80
P_LOCKED = 0.20

# Exact integer pattern counts per chest state from Fruit's d2pg generator
# (also documented and weighted at https://d2runes.io/rune-farming/lk-farming):
# Format: Rune: (unlocked_count, locked_count)
PATTERNS_P7 = {
    "Pul": (16, 16),  # weighted: 16.0
    "Um":  (10, 11),  # weighted: 10.2
    "Mal": (14, 15),  # weighted: 14.2
    "Ist": (5,  7),   # weighted: 5.4
    "Gul": (11, 11),  # weighted: 11.0
    "Vex": (6,  6),   # weighted: 6.0
    "Ohm": (5,  5),   # weighted: 5.0
    "Lo":  (2,  2),   # weighted: 2.0
    "Sur": (9,  9),   # weighted: 9.0
    "Ber": (2,  2),   # weighted: 2.0
}

PATTERNS_P5 = {
    "Pul": (16, 18),  # weighted: 16.4
    "Um":  (11, 11),  # weighted: 11.0
    "Mal": (10, 10),  # weighted: 10.0
    "Ist": (5,  6),   # weighted: 5.2
    "Gul": (5,  5),   # weighted: 5.0
    "Vex": (6,  6),   # weighted: 6.0
    "Ohm": (2,  2),   # weighted: 2.0
    "Lo":  (4,  4),   # weighted: 4.0
    "Sur": (5,  7),   # weighted: 5.4
    "Ber": (4,  4),   # weighted: 4.0
}

PATTERNS_P3 = {
    "Pul": (12, 14),  # weighted: 12.4
    "Um":  (7,  9),   # weighted: 7.4
    "Mal": (12, 12),  # weighted: 12.0
    "Ist": (8,  10),  # weighted: 8.4
    "Gul": (4,  6),   # weighted: 4.4
    "Vex": (3,  3),   # weighted: 3.0
    "Ohm": (2,  2),   # weighted: 2.0
    "Lo":  (4,  4),   # weighted: 4.0
    "Sur": (4,  5),   # weighted: 4.2
    "Ber": (2,  2),   # weighted: 2.0
}

PATTERNS_P1 = {
    "Pul": (9,  9),   # weighted: 9.0
    "Um":  (8,  8),   # weighted: 8.0
    "Mal": (9,  9),   # weighted: 9.0
    "Ist": (4,  5),   # weighted: 4.2
    "Gul": (6,  6),   # weighted: 6.0
    "Vex": (2,  2),   # weighted: 2.0
    "Ohm": (4,  4),   # weighted: 4.0
    "Lo":  (3,  3),   # weighted: 3.0
    "Sur": (2,  3),   # weighted: 2.2
    "Ber": (1,  1),   # weighted: 1.0
}

RUNE_ORDER = ["Pul", "Um", "Mal", "Ist", "Gul", "Vex", "Ohm", "Lo", "Sur", "Ber"]


def weighted_patterns(table, p_lock=0.20):
    return {
        r: (1.0 - p_lock) * u + p_lock * l
        for r, (u, l) in table.items()
    }


def absorbing_markov_expected_runs(
    w_patterns: dict,
    target_rune: str,
    min_cube_rune: str = "Pul",
    chests_per_run: int = 6,
    total_patterns: int = TOTAL_PATTERNS,
):
    """
    Compute the exact expected number of 6-chest runs and full CDF of the number
    of runs needed to acquire at least 1 `target_rune` by cubing all runes from
    `min_cube_rune` up to `target_rune`.

    Because 2 of rune i cube into 1 of rune i+1 for every rune from Pul (#21) to Ber (#30):
    Each rune r in [min_cube_rune, ..., target_rune] has an exact integer weight
    w_r = 2^(idx(r) - idx(min_cube_rune)) in units of `min_cube_rune`,
    and the target threshold is W = 2^(idx(target_rune) - idx(min_cube_rune))!
    Wait: since every single upgrade from Pul -> Um -> Mal -> Ist -> Gul -> Vex -> Ohm -> Lo -> Sur -> Ber
    requires exactly 2 runes of tier i to make 1 rune of tier i+1,
    any collection of runes below `target_rune` can be cubed into `target_rune`
    if and only if their total binary value >= W = 2^(idx_target - idx_min)!
    (Proof: by binary representation, a sum of powers of 2 from {2^0, 2^1, ..., 2^K}
    is >= 2^K if and only if we can greedily pair identical powers of 2 upward to form 2^K!)
    """
    idx_min = RUNE_ORDER.index(min_cube_rune)
    idx_target = RUNE_ORDER.index(target_rune)
    assert idx_min <= idx_target

    K = idx_target - idx_min
    W = 1 << K  # Target value in units of min_cube_rune

    # Single chest transition probabilities over value increments
    # State space is {0, 1, ..., W}, where W is absorbing.

    # Wait: if target_rune is e.g. "Lo", you CANNOT cube a Sur or Ber down into a Lo!
    # So only runes r with idx_min <= idx(r) <= idx_target contribute to cubing `target_rune`!
    step_probs = {}
    p_useful = 0.0
    for idx in range(idx_min, idx_target + 1):
        r = RUNE_ORDER[idx]
        val = 1 << (idx - idx_min)
        p_r = w_patterns[r] / total_patterns
        step_probs[val] = step_probs.get(val, 0.0) + p_r
        p_useful += p_r
    step_probs[0] = 1.0 - p_useful

    # Build the transient transition matrix Q of size W x W for a SINGLE chest
    # Since all transitions are forward (i -> min(W, i + val)), I - Q is upper triangular!
    # We can solve for expected chests (and expected runs) in O(W * K) time exactly!
    # Wait: for 6 chests per run, the 1-run transition distribution is the 6-fold convolution
    # of step_probs (capped at W), or even simpler: we can compute the exact 6-chest run
    # step distribution by convolving step_probs 6 times!
    run_probs = {0: 1.0}
    for _ in range(chests_per_run):
        new_probs = {}
        for v1, p1 in run_probs.items():
            for v2, p2 in step_probs.items():
                v_sum = min(W, v1 + v2)
                new_probs[v_sum] = new_probs.get(v_sum, 0.0) + p1 * p2
        run_probs = new_probs

    # Expected number of runs E[R_i] starting from state i in {0, 1, ..., W-1}:
    # E[R_i] = 1 + sum_{v > 0, i+v < W} run_probs[v] * E[R_{i+v}] + run_probs[0] * E[R_i]
    # => (1 - run_probs[0]) * E[R_i] = 1 + sum_{v > 0, i+v < W} run_probs[v] * E[R_{i+v}]
    E_runs = np.zeros(W + 1)
    p0 = run_probs[0]
    for i in range(W - 1, -1, -1):
        acc = 1.0
        for v, pv in run_probs.items():
            if v > 0 and i + v < W:
                acc += pv * E_runs[i + v]
        E_runs[i] = acc / (1.0 - p0)

    # Also compute Variance Var[R_0] using second moment E[R_i^2]:
    # R_i = 1 + R_{i + V}, so R_i^2 = 1 + 2 R_{i + V} + R_{i + V}^2
    # E[R_i^2] = 1 + 2 * sum_{v} pv * E[R_{i+v}] + sum_{v} pv * E[R_{i+v}^2]
    # Note: 1 + sum_{v} pv * E[R_{i+v}] = E[R_i], so:
    # E[R_i^2] = 2 * E[R_i] - 1 + sum_{v} pv * E[R_{i+v}^2]
    E_runs_sq = np.zeros(W + 1)
    for i in range(W - 1, -1, -1):
        acc = 2.0 * E_runs[i] - 1.0
        for v, pv in run_probs.items():
            if v > 0 and i + v < W:
                acc += pv * E_runs_sq[i + v]
        E_runs_sq[i] = acc / (1.0 - p0)

    var_runs = E_runs_sq[0] - E_runs[0] ** 2
    sd_runs = math.sqrt(max(0.0, var_runs))
    return E_runs[0], sd_runs, run_probs


def compute_cdf_curves(w_patterns: dict, target_rune: str, min_cube_rune: str = "Pul", max_runs: int = 3500, chests_per_run: int = 6, total_patterns: int = TOTAL_PATTERNS):
    """
    Compute the exact cumulative distribution function F(n) = P(R <= n)
    for n = 0, 1, ..., max_runs by evolving the state distribution vector
    over {0, 1, ..., W}.
    """
    idx_min = RUNE_ORDER.index(min_cube_rune)
    idx_target = RUNE_ORDER.index(target_rune)
    K = idx_target - idx_min
    W = 1 << K

    step_probs = {}
    p_useful = 0.0
    for idx in range(idx_min, idx_target + 1):
        r = RUNE_ORDER[idx]
        val = 1 << (idx - idx_min)
        p_r = w_patterns[r] / total_patterns
        step_probs[val] = step_probs.get(val, 0.0) + p_r
        p_useful += p_r
    step_probs[0] = 1.0 - p_useful

    # Evolve per chest for 6 * max_runs chests, recording after every 6 chests
    state = np.zeros(W + 1)
    state[0] = 1.0
    cdf = np.zeros(max_runs + 1)

    # Pre-extract non-zero jumps
    jumps = [(v, pv) for v, pv in step_probs.items() if v > 0]
    p0 = step_probs[0]

    for r in range(1, max_runs + 1):
        for _ in range(chests_per_run):
            new_state = p0 * state
            new_state[W] = state[W]  # absorbing state stays at W
            for v, pv in jumps:
                # states 0 .. W-v-1 shift by +v
                if W - v > 0:
                    new_state[v:W] += pv * state[0:W - v]
                # states W-v .. W-1 get absorbed into W
                new_state[W] += pv * np.sum(state[max(0, W - v):W])
            state = new_state
        cdf[r] = state[W]
    return cdf


def absorbing_markov_expected_runs_multiple(
    w_patterns: dict,
    target_rune: str,
    target_copies: int = 1,
    min_cube_rune: str = "Pul",
    chests_per_run: int = 6,
    total_patterns: int = TOTAL_PATTERNS,
):
    """
    Compute the exact expected number of 6-chest runs and SD(R) to acquire
    `target_copies` of `target_rune` (e.g., 1 Ber = 1, 2 Ber = Infinity = 2,
    Enigma = 1 Jah + 1 Ber = 3 Ber equivalents) by cubing from `min_cube_rune`.
    """
    idx_min = RUNE_ORDER.index(min_cube_rune)
    idx_target = RUNE_ORDER.index(target_rune)
    K = idx_target - idx_min
    W = target_copies * (1 << K)

    step_probs = {}
    p_useful = 0.0
    for idx in range(idx_min, idx_target + 1):
        r = RUNE_ORDER[idx]
        val = 1 << (idx - idx_min)
        p_r = w_patterns[r] / total_patterns
        step_probs[val] = step_probs.get(val, 0.0) + p_r
        p_useful += p_r
    step_probs[0] = 1.0 - p_useful

    run_probs = {0: 1.0}
    for _ in range(chests_per_run):
        new_probs = {}
        for v1, p1 in run_probs.items():
            for v2, p2 in step_probs.items():
                v_sum = min(W, v1 + v2)
                new_probs[v_sum] = new_probs.get(v_sum, 0.0) + p1 * p2
        run_probs = new_probs

    E_runs = np.zeros(W + 1)
    E_runs_sq = np.zeros(W + 1)
    p0 = run_probs[0]
    for i in range(W - 1, -1, -1):
        acc = 1.0
        for v, pv in run_probs.items():
            if v > 0 and i + v < W:
                acc += pv * E_runs[i + v]
        E_runs[i] = acc / (1.0 - p0)

        acc_sq = 2.0 * E_runs[i] - 1.0
        for v, pv in run_probs.items():
            if v > 0 and i + v < W:
                acc_sq += pv * E_runs_sq[i + v]
        E_runs_sq[i] = acc_sq / (1.0 - p0)

    sd_runs = math.sqrt(max(0.0, E_runs_sq[0] - E_runs[0] ** 2))

    # Also compare to the naive fluid/drift approximation:
    # W / E[Delta V_run] (which ignores overshoot at the absorbing boundary!)
    expected_val_per_chest = sum(
        (1 << (idx - idx_min)) * (w_patterns[RUNE_ORDER[idx]] / total_patterns)
        for idx in range(idx_min, idx_target + 1)
    )
    naive_runs = W / (chests_per_run * expected_val_per_chest)
    return E_runs[0], sd_runs, naive_runs


if __name__ == "__main__":
    w7 = weighted_patterns(PATTERNS_P7, 0.20)
    w5 = weighted_patterns(PATTERNS_P5, 0.20)

    print("=== Weighted Vex-Ber totals (20% locked, 80% unlocked) ===")
    vex_ber_7 = sum(w7[r] for r in ["Vex", "Ohm", "Lo", "Sur", "Ber"])
    vex_ber_5 = sum(w5[r] for r in ["Vex", "Ohm", "Lo", "Sur", "Ber"])
    print(f"/players 7 Vex-Ber patterns: {vex_ber_7:.1f} / {TOTAL_PATTERNS}")
    p_run_7 = 1.0 - (1.0 - vex_ber_7 / TOTAL_PATTERNS) ** 6
    print(f"/players 7 p_run = {p_run_7:.8f} (1 in {1/p_run_7:.2f} runs)")
    for n in [1000, 1500]:
        s = (1.0 - p_run_7) ** n
        print(f"  S({n}) = {s*100:.2f}% (1 in {1/s:.1f})")

    print("\n=== Expected Runs to Target Rune (Direct vs Cubing from Gul+ vs Pul+) ===")
    targets = ["Mal", "Ist", "Gul", "Vex", "Ohm", "Lo", "Sur", "Ber"]
    idx_gul = RUNE_ORDER.index("Gul")
    idx_vex = RUNE_ORDER.index("Vex")
    for target in targets:
        print(f"\nTarget: {target}")
        idx_target = RUNE_ORDER.index(target)
        for label, w in [("/players 7", w7), ("/players 5", w5)]:
            e_direct, sd_direct, _ = absorbing_markov_expected_runs(w, target, target)
            e_pul, sd_pul, _ = absorbing_markov_expected_runs(w, target, "Pul")
            if idx_target >= idx_gul:
                e_gul, sd_gul, _ = absorbing_markov_expected_runs(w, target, "Gul")
                gul_str = f"Cube Gul+ = {e_gul:7.1f} | "
            else:
                gul_str = "Cube Gul+ =     --- | "

            if idx_target >= idx_vex:
                e_vex, sd_vex, _ = absorbing_markov_expected_runs(w, target, "Vex")
                vex_str = f"Cube Vex+ = {e_vex:7.1f} | "
            else:
                vex_str = ""

            print(
                f"  {label}: Direct = {e_direct:7.1f} (SD {sd_direct:6.1f}) | "
                f"{vex_str}{gul_str}"
                f"Cube Pul+ = {e_pul:7.1f} (SD {sd_pul:6.1f})"
            )

    print("\n=== First-Order Stochastic Dominance & Quantiles (Mal through Ber) ===")
    for r in ["Mal", "Ist", "Gul", "Lo"]:
        cdf_p7 = compute_cdf_curves(w7, r, "Pul", 4000)
        cdf_p5 = compute_cdf_curves(w5, r, "Pul", 4000)
        med_p7 = int(np.searchsorted(cdf_p7, 0.5))
        med_p5 = int(np.searchsorted(cdf_p5, 0.5))
        p90_p7 = int(np.searchsorted(cdf_p7, 0.9))
        p90_p5 = int(np.searchsorted(cdf_p5, 0.9))
        print(f"  {r:3s} (cubing Pul+):")
        print(f"    /players 7: Median = {med_p7:4d} runs, 90th pct = {p90_p7:4d} runs")
        print(f"    /players 5: Median = {med_p5:4d} runs, 90th pct = {p90_p5:4d} runs")

    # Compare Lo CDF breakdown on /players 7 vs /players 5 (cubing Pul+)
    cdf_lo_p7 = compute_cdf_curves(w7, "Lo", "Pul", 4000)
    cdf_lo_p5 = compute_cdf_curves(w5, "Lo", "Pul", 4000)
    print("\nLo Crossover Breakdown by Run Milestone:")
    for n in [1000, 1500, 2000, 2500, 3000]:
        print(f"  By {n:4d} runs: P(Lo | /p7) = {cdf_lo_p7[n]*100:5.2f}% vs P(Lo | /p5) = {cdf_lo_p5[n]*100:5.2f}%")

    print("\n=== Base Ladder Mid-Runes: Pul (#21) and Um (#22) ===")
    for r in ["Pul", "Um"]:
        e_dir_7, _, _ = absorbing_markov_expected_runs(w7, r, r)
        e_dir_5, _, _ = absorbing_markov_expected_runs(w5, r, r)
        e_pul_7, sd_pul_7, _ = absorbing_markov_expected_runs(w7, r, "Pul")
        e_pul_5, sd_pul_5, _ = absorbing_markov_expected_runs(w5, r, "Pul")
        print(f"  {r:3s}: /p7 Direct = {e_dir_7:6.1f} (Cube Pul+ = {e_pul_7:6.1f}, SD {sd_pul_7:5.1f}) | /p5 Direct = {e_dir_5:6.1f} (Cube Pul+ = {e_pul_5:6.1f}, SD {sd_pul_5:5.1f})")

    print("\n=== Exact Markov vs Naive Drift Approximation (Overshoot Penalty) on /players 7 (Pul+) ===")
    for r in ["Mal", "Ist", "Gul", "Vex", "Ohm", "Lo", "Sur", "Ber"]:
        e_exact, sd_exact, e_naive = absorbing_markov_expected_runs_multiple(w7, r, 1, "Pul")
        print(f"  1x {r:3s}: Exact Markov E[R] = {e_exact:7.1f} (SD {sd_exact:6.1f}) | Naive Drift = {e_naive:7.1f} | Overshoot = +{e_exact - e_naive:5.1f} runs (+{(e_exact/e_naive - 1)*100:4.1f}%)")
    for copies, name in [(2, "Infinity (2x Ber)"), (3, "Enigma (3x Ber = Jah+Ber)")]:
        e7, sd7, n7 = absorbing_markov_expected_runs_multiple(w7, "Ber", copies, "Pul")
        e5, sd5, n5 = absorbing_markov_expected_runs_multiple(w5, "Ber", copies, "Pul")
        print(f"  {name:26s} (/p7 Pul+): Exact = {e7:7.1f} (SD {sd7:6.1f}), Naive = {n7:7.1f} | (/p5 Pul+): Exact = {e5:7.1f} (SD {sd5:6.1f})")
