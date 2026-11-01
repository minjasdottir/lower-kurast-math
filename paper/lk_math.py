#!/usr/bin/env python3
"""
Exact probabilistic analysis of Diablo II: Resurrected Lower Kurast (LK)
superchest runs on /players 7-8.
"""

import math

TOTAL_PATTERNS = 65534  # 2^16 - 2 valid superchest patterns in 1.13c+ / D2R

# High rune pattern counts on /players 7 in Lower Kurast superchests
# Grounded in Fruit's (bonqen / d2pg) reverse-engineered locked/unlocked model
# (80% unlocked + 20% locked), verified against clean vanilla binaries by fearedbliss.
# Documented and weighted by TheHappyDev at https://d2runes.io/rune-farming/lk-farming
RUNE_PATTERNS_P7 = {
    "Pul": 16.0,
    "Um": 10.2,
    "Mal": 14.2,
    "Ist": 5.4,
    "Gul": 11.0,
    "Vex": 6.0,
    "Ohm": 5.0,
    "Lo": 2.0,
    "Sur": 9.0,
    "Ber": 2.0,
}

VEX_TO_BER_PATTERNS = sum(
    RUNE_PATTERNS_P7[r] for r in ["Vex", "Ohm", "Lo", "Sur", "Ber"]
)
GUL_TO_BER_PATTERNS = VEX_TO_BER_PATTERNS + RUNE_PATTERNS_P7["Gul"]
PUL_TO_BER_PATTERNS = sum(RUNE_PATTERNS_P7.values())


def prob_at_least_one_in_run(k_patterns: int, chests_per_run: int = 6) -> float:
    p_chest = k_patterns / TOTAL_PATTERNS
    return 1.0 - (1.0 - p_chest) ** chests_per_run


def dry_spell_prob(p_run: float, n_runs: int) -> float:
    return (1.0 - p_run) ** n_runs


def normal_tail_sigma(prob: float) -> float:
    """
    Convert a one-sided tail probability P(Z >= z) = prob (or two-sided)
    into standard normal sigma units using inverse erf.
    Here we report both one-sided z (P(Z > z) = prob) and two-sided z (P(|Z| > z) = prob).
    """
    # Using math.erfc: P(Z > z) = 0.5 * erfc(z / sqrt(2))
    # Binary search for z > 0
    lo, hi = 0.0, 10.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        val = 0.5 * math.erfc(mid / math.sqrt(2.0))
        if val > prob:
            lo = mid
        else:
            hi = mid
    z_one_sided = 0.5 * (lo + hi)

    lo, hi = 0.0, 10.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        val = math.erfc(mid / math.sqrt(2.0))
        if val > prob:
            lo = mid
        else:
            hi = mid
    z_two_sided = 0.5 * (lo + hi)
    return z_one_sided, z_two_sided


def main():
    p_chest = VEX_TO_BER_PATTERNS / TOTAL_PATTERNS
    p_run = prob_at_least_one_in_run(VEX_TO_BER_PATTERNS, 6)
    expected_runs = 1.0 / p_run
    std_runs = math.sqrt(1.0 - p_run) / p_run
    median_runs = math.ceil(math.log(0.5) / math.log(1.0 - p_run))

    print("=== Vex-Ber on /players 7-8 (6 superchests per run) ===")
    print(f"Patterns per chest: {VEX_TO_BER_PATTERNS} / {TOTAL_PATTERNS}")
    print(f"p_chest = {p_chest:.8f} (1 in {1/p_chest:.2f} chests)")
    print(f"p_run (6 chests) = {p_run:.8f} (1 in {1/p_run:.2f} runs)")
    print(f"Expected runs E[T] = {expected_runs:.2f}")
    print(f"Std dev SD[T] = {std_runs:.2f}")
    print(f"Median runs = {median_runs}")
    print()

    for n in [405, 456, 800, 1000, 1500, 2000, 2460, 2461]:
        p_dry = dry_spell_prob(p_run, n)
        z1, z2 = normal_tail_sigma(p_dry)
        z_linear = (n - expected_runs) / std_runs
        print(
            f"N = {n:4d} runs: P(T > {n}) = {p_dry*100:6.3f}% "
            f"(1 in {1/p_dry:5.1f}) | linear z = {z_linear:5.2f} | "
            f"normal eq: {z1:.2f} sigma (1-sided), {z2:.2f} sigma (2-sided)"
        )
        for m in [10, 15]:
            p_career = 1.0 - (1.0 - p_dry) ** m
            print(f"    Across M = {m} HRs: P(max T_i > {n}) = {p_career*100:5.2f}%")


if __name__ == "__main__":
    main()
