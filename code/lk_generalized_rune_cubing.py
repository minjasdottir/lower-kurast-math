#!/usr/bin/env python3
"""
lk_generalized_rune_cubing.py
-----------------------------
Generalized discrete absorbing Markov chain engine for Lower Kurast (LK) superchests
under Fruit's (bonqen) reverse-engineered drop model (d2pg) verified by fearedbliss.

Supports:
- Arbitrary initial player stash / inventory (e.g. {'Ist': 1, 'Gul': 1, 'Pul': 2})
- Target runes (e.g. 'Vex', 'Ohm', 'Lo', 'Sur', 'Ber', '2x Ber', 'Cham')
- Major runewords (e.g. 'Call to Arms', 'Heart of the Oak', 'Grief', 'Infinity', 'Enigma', 'Fortitude')
- Automatic runeword slot reservation (allocates matching mid-runes to support slots,
  applies surplus value to the headliner cubing ladder)
- Exact remaining expected runs, standard deviation, and full quantile distribution
  (Median 50%, 75th, 90th, 95th, 99th percentiles)
- Runs saved and progress percentage gained from the starting stash
- Real-world time estimates across farming speeds (20s, 25s, 30s per run)
- Expected collateral drops of missing support runes over the remaining runs
"""

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

# Total 16-bit truncated seed patterns: 2^16 - 2 = 65,534
TOTAL_PATTERNS = 65534

# Standard chest lock probability in Hell Lower Kurast (alvl = 80)
DEFAULT_P_LOCK = 0.20

# Integer pattern counts per chest state from Fruit's d2pg generator
# Format: Rune: (unlocked_count, locked_count)
PATTERNS_TABLES = {
    "p7": {
        "Pul": (16, 16),
        "Um":  (10, 11),
        "Mal": (14, 15),
        "Ist": (5,  7),
        "Gul": (11, 11),
        "Vex": (6,  6),
        "Ohm": (5,  5),
        "Lo":  (2,  2),
        "Sur": (9,  9),
        "Ber": (2,  2),
    },
    "p5": {
        "Pul": (16, 18),
        "Um":  (11, 11),
        "Mal": (10, 10),
        "Ist": (5,  6),
        "Gul": (5,  5),
        "Vex": (6,  6),
        "Ohm": (2,  2),
        "Lo":  (4,  4),
        "Sur": (5,  7),
        "Ber": (4,  4),
    },
    "p3": {
        "Pul": (12, 14),
        "Um":  (7,  9),
        "Mal": (12, 12),
        "Ist": (8,  10),
        "Gul": (8,  10),
        "Vex": (4,  6),
        "Ohm": (3,  3),
        "Lo":  (2,  2),
        "Sur": (4,  5),
        "Ber": (2,  2),
    },
    "p1": {
        "Pul": (9,  9),
        "Um":  (8,  8),
        "Mal": (9,  9),
        "Ist": (4,  5),
        "Gul": (6,  6),
        "Vex": (2,  2),
        "Ohm": (4,  4),
        "Lo":  (3,  3),
        "Sur": (2,  3),
        "Ber": (1,  1),
    },
}

RUNE_ORDER = ["Pul", "Um", "Mal", "Ist", "Gul", "Vex", "Ohm", "Lo", "Sur", "Ber"]

# Runeword registry for major progression and endgame targets
RUNEWORDS: Dict[str, dict] = {
    "Heart of the Oak": {
        "aliases": ["hoto", "heart of the oak"],
        "recipe_runes": {"Vex": 1},
        "support_runes": {"Pul": 1},
        "sub_pul_runes": ["Ko", "Thul"],
        "recipe_text": "Ko + Vex + Pul + Thul (4-socket Flail/Staff)",
    },
    "Call to Arms": {
        "aliases": ["cta", "call to arms"],
        "recipe_runes": {"Ohm": 1},
        "support_runes": {"Mal": 1, "Ist": 1},
        "sub_pul_runes": ["Amn", "Ral"],
        "recipe_text": "Amn + Ral + Mal + Ist + Ohm (5-socket Weapon)",
    },
    "Grief": {
        "aliases": ["grief"],
        "recipe_runes": {"Lo": 1},
        "support_runes": {"Mal": 1},
        "sub_pul_runes": ["Eth", "Tir", "Ral"],
        "recipe_text": "Eth + Tir + Lo + Mal + Ral (5-socket Sword/Axe)",
    },
    "Fortitude": {
        "aliases": ["fort", "fortitude"],
        "recipe_runes": {"Lo": 1},
        "support_runes": {},
        "sub_pul_runes": ["El", "Sol", "Dol"],
        "recipe_text": "El + Sol + Dol + Lo (4-socket Armor/Weapon)",
    },
    "Infinity": {
        "aliases": ["infinity"],
        "recipe_runes": {"Ber": 2},
        "support_runes": {"Mal": 1, "Ist": 1},
        "sub_pul_runes": [],
        "recipe_text": "Ber + Mal + Ber + Ist (4-socket Polearm/Spear)",
    },
    "Enigma": {
        "aliases": ["enigma"],
        "recipe_runes": {"Ber": 3},  # In LK, Jah (2 Ber) + Ber = 3 Ber equivalents
        "support_runes": {},
        "sub_pul_runes": ["Ith"],
        "recipe_text": "Jah + Ith + Ber (3-socket Armor; 3 Ber eq in LK)",
    },
    "Mosaic": {
        "aliases": ["mosaic"],
        "recipe_runes": {"Gul": 1},
        "support_runes": {"Mal": 1},
        "sub_pul_runes": ["Thul"],
        "recipe_text": "Mal + Gul + Thul (3-socket Claw)",
    },
    "Chains of Honor": {
        "aliases": ["coh", "chains of honor"],
        "recipe_runes": {"Ber": 1},
        "support_runes": {"Ist": 1, "Um": 1},
        "sub_pul_runes": ["Dol"],
        "recipe_text": "Dol + Um + Ber + Ist (4-socket Armor)",
    },
    "Death": {
        "aliases": ["death"],
        "recipe_runes": {"Vex": 1, "Gul": 1},
        "support_runes": {},
        "sub_pul_runes": ["Hel", "El", "Ort"],
        "recipe_text": "Hel + El + Vex + Ort + Gul (5-socket Sword/Axe)",
    },
    "Faith": {
        "aliases": ["faith"],
        "recipe_runes": {"Ber": 2, "Ohm": 1},  # Jah = 2x Ber in LK
        "support_runes": {},
        "sub_pul_runes": ["Lem", "Eld"],
        "recipe_text": "Ohm + Jah + Lem + Eld (4-socket Bow/Crossbow; Jah = 2 Ber eq in LK)",
    },
    "Phoenix": {
        "aliases": ["phoenix"],
        "recipe_runes": {"Ber": 2, "Lo": 1, "Vex": 2},  # Jah = 2x Ber in LK
        "support_runes": {},
        "sub_pul_runes": [],
        "recipe_text": "Vex + Vex + Lo + Jah (4-socket Shield/Weapon; Jah = 2 Ber eq in LK)",
    },
    "Dream": {
        "aliases": ["dream"],
        "recipe_runes": {"Ber": 2},  # Jah = 2x Ber in LK
        "support_runes": {"Pul": 1},
        "sub_pul_runes": ["Io"],
        "recipe_text": "Io + Jah + Pul (3-socket Helm/Shield; Jah = 2 Ber eq in LK)",
    },
    "Beast": {
        "aliases": ["beast"],
        "recipe_runes": {"Ber": 1},
        "support_runes": {"Mal": 1, "Um": 1},
        "sub_pul_runes": ["Tir", "Lum"],
        "recipe_text": "Ber + Tir + Um + Mal + Lum (5-socket Axe/Hammer/Scepter)",
    },
    "Ice": {
        "aliases": ["ice"],
        "recipe_runes": {"Ber": 2, "Lo": 1},  # Jah = 2x Ber in LK
        "support_runes": {},
        "sub_pul_runes": ["Amn", "Shael"],
        "recipe_text": "Amn + Shael + Jah + Lo (4-socket Bow; Jah = 2 Ber eq in LK)",
    },
    "Brand": {
        "aliases": ["brand"],
        "recipe_runes": {"Ber": 2, "Lo": 1, "Gul": 1},  # Jah = 2x Ber in LK
        "support_runes": {"Mal": 1},
        "sub_pul_runes": [],
        "recipe_text": "Jah + Lo + Mal + Gul (4-socket Crossbow/Bow; Jah = 2 Ber eq in LK)",
    },
    "Eternity": {
        "aliases": ["eternity"],
        "recipe_runes": {"Ber": 1, "Sur": 1},
        "support_runes": {"Ist": 1},
        "sub_pul_runes": ["Amn", "Sol"],
        "recipe_text": "Amn + Ber + Ist + Sol + Sur (5-socket Melee/Missile Weapon)",
    },
}


def weighted_patterns(table: dict, p_lock: float = DEFAULT_P_LOCK) -> Dict[str, float]:
    """Calculate effective patterns per chest weighting unlocked (1-p) and locked (p)."""
    return {
        r: (1.0 - p_lock) * u + p_lock * l
        for r, (u, l) in table.items()
    }


def rune_valuation_in_units(rune: str, min_rune: str = "Pul") -> int:
    """Return integer binary value of a rune in units of min_rune (where 2 of tier i = 1 of i+1)."""
    idx_min = RUNE_ORDER.index(min_rune)
    idx_r = RUNE_ORDER.index(rune)
    if idx_r < idx_min:
        return 0
    return 1 << (idx_r - idx_min)


@dataclass
class StashAllocation:
    """Breakdown of how user stash was allocated."""
    recipe_runes: Dict[str, int] = field(default_factory=dict)
    reserved_recipe: Dict[str, int] = field(default_factory=dict)
    missing_recipe: Dict[str, int] = field(default_factory=dict)
    reserved_support: Dict[str, int] = field(default_factory=dict)
    missing_support: Dict[str, int] = field(default_factory=dict)
    surplus_runes_for_cubing: Dict[str, int] = field(default_factory=dict)
    unusable_higher_runes: Dict[str, int] = field(default_factory=dict)
    sub_min_runes: Dict[str, int] = field(default_factory=dict)
    initial_valuation_units: int = 0
    target_threshold_units: int = 0
    baseline_threshold_units: int = 0
    max_useful_rune: str = "Ber"
    target_description: str = ""
    headliner: str = "Ber"
    headliner_copies: int = 1


@dataclass
class Quantiles:
    p50_median: int
    p75: int
    p90: int
    p95: int
    p99: int


@dataclass
class TimeEstimates:
    hours_20s: float
    hours_25s: float
    hours_30s: float


@dataclass
class CollateralExpectation:
    rune: str
    needed: int
    expected_drops: float
    prob_at_least_needed: float


@dataclass
class AnalysisResult:
    target_name: str
    target_type: str  # 'runeword' or 'rune'
    player_setting: str
    chests_per_run: int
    min_cube_rune: str
    allocation: StashAllocation
    
    # Markov chain metrics
    expected_runs: float
    std_dev_runs: float
    baseline_expected_runs: float
    runs_saved: float
    pct_progress: float
    
    quantiles: Quantiles
    times: TimeEstimates
    collateral_drops: List[CollateralExpectation] = field(default_factory=list)
    recipe_runes: Optional[str] = None


def resolve_target(target_input: str) -> Tuple[str, Dict[str, int], Dict[str, int], List[str], str, str]:
    """
    Resolve user string input into:
    (canonical_name, recipe_runes, support_runes, sub_pul_runes, recipe_text, target_type).
    Supports runeword names, aliases, single runes, multiplier syntax ('2x Ber'),
    or composite rune combinations ('Ber + Sur', '1 Ber, 1 Sur').
    """
    cleaned = target_input.strip()
    lowered = cleaned.lower()

    # 1. Check runewords
    for rw_name, data in RUNEWORDS.items():
        if lowered == rw_name.lower() or lowered in [a.lower() for a in data["aliases"]]:
            return (
                rw_name,
                dict(data["recipe_runes"]),
                dict(data["support_runes"]),
                list(data["sub_pul_runes"]),
                data["recipe_text"],
                "runeword"
            )

    # 2. Check composite or multiplier rune syntax: e.g. "Ber + Sur", "2x Ber", "Ber*2"
    tokens = [x.strip() for x in re.split(r"[,+&]+", cleaned) if x.strip()]
    if tokens:
        res: Dict[str, int] = {}
        all_valid = True
        for tok in tokens:
            m1 = re.match(r"^(\d+)\s*[xX*]?\s*([A-Za-z]+)$", tok)
            if m1:
                cnt = int(m1.group(1))
                r = m1.group(2).capitalize()
                if r in RUNE_ORDER:
                    res[r] = res.get(r, 0) + cnt
                    continue
            m2 = re.match(r"^([A-Za-z]+)\s*[:=\s]\s*(\d+)$", tok)
            if m2:
                r = m2.group(1).capitalize()
                cnt = int(m2.group(2))
                if r in RUNE_ORDER:
                    res[r] = res.get(r, 0) + cnt
                    continue
            r = tok.capitalize()
            if r in RUNE_ORDER:
                res[r] = res.get(r, 0) + 1
                continue
            all_valid = False
            break

        if all_valid and res:
            if len(res) == 1 and next(iter(res.values())) == 1:
                canonical = next(iter(res.keys()))
            elif len(res) == 1:
                r, cnt = next(iter(res.items()))
                canonical = f"{cnt}x {r}"
            else:
                canonical = " + ".join(f"{cnt}x {r}" if cnt > 1 else r for r, cnt in res.items())
            return canonical, res, {}, [], f"{canonical} (Target runes)", "rune"

    raise ValueError(f"Unknown target: '{target_input}'. Must be a rune (e.g. 'Vex', '2x Ber', 'Ber + Sur') or known runeword (e.g. 'Call to Arms').")


def allocate_stash(
    target_name: str,
    recipe_runes: Dict[str, int],
    support_runes: Dict[str, int],
    current_stash: Dict[str, int],
    min_cube_rune: str = "Pul"
) -> StashAllocation:
    """
    Intelligently allocate user stash:
    1. Satisfy required support runes first (e.g., Ist and Mal for CTA).
    2. Satisfy matching recipe runes (dedicated sockets reserved, e.g. 1 Sur for Eternity).
    3. Any surplus runes below or equal to max useful rune contribute to the cubing ladder.
    4. Runes higher than max useful rune are categorized as unusable downward.
    """
    alloc = StashAllocation(recipe_runes=dict(recipe_runes))
    remaining_stash = {r.capitalize(): cnt for r, cnt in current_stash.items() if cnt > 0}
    idx_min = RUNE_ORDER.index(min_cube_rune)

    # 1. Fill support slots first
    for sup_rune, needed in support_runes.items():
        sup_cap = sup_rune.capitalize()
        have = remaining_stash.get(sup_cap, 0)
        reserved = min(have, needed)
        missing = needed - reserved
        if reserved > 0:
            alloc.reserved_support[sup_cap] = reserved
            remaining_stash[sup_cap] -= reserved
            if remaining_stash[sup_cap] == 0:
                del remaining_stash[sup_cap]
        if missing > 0:
            alloc.missing_support[sup_cap] = missing

    # 2. Fill recipe slots (reserved sockets)
    for rec_rune, needed in recipe_runes.items():
        rec_cap = rec_rune.capitalize()
        have = remaining_stash.get(rec_cap, 0)
        reserved = min(have, needed)
        missing = needed - reserved
        if reserved > 0:
            alloc.reserved_recipe[rec_cap] = reserved
            remaining_stash[rec_cap] -= reserved
            if remaining_stash[rec_cap] == 0:
                del remaining_stash[rec_cap]
        if missing > 0:
            alloc.missing_recipe[rec_cap] = missing

    # Determine max useful rune tier for this target
    max_idx = max(RUNE_ORDER.index(r) for r in recipe_runes.keys()) if recipe_runes else len(RUNE_ORDER) - 1
    alloc.max_useful_rune = RUNE_ORDER[max_idx]
    alloc.headliner = alloc.max_useful_rune
    alloc.headliner_copies = recipe_runes.get(alloc.max_useful_rune, 1)

    # Format description of target
    alloc.target_description = " + ".join(f"{cnt}x {r}" if cnt > 1 else r for r, cnt in recipe_runes.items())

    # 3. Process remaining surplus stash
    unit_sum = 0
    for r_name, count in remaining_stash.items():
        if count <= 0:
            continue
        if r_name not in RUNE_ORDER:
            alloc.sub_min_runes[r_name] = count
            continue

        r_idx = RUNE_ORDER.index(r_name)
        if r_idx < idx_min:
            alloc.sub_min_runes[r_name] = count
        elif r_idx > max_idx:
            alloc.unusable_higher_runes[r_name] = count
        else:
            alloc.surplus_runes_for_cubing[r_name] = count
            unit_sum += count * (1 << (r_idx - idx_min))

    baseline_threshold = sum(cnt * (1 << (RUNE_ORDER.index(r) - idx_min)) for r, cnt in recipe_runes.items())
    target_threshold = sum(cnt * (1 << (RUNE_ORDER.index(r) - idx_min)) for r, cnt in alloc.missing_recipe.items())
    alloc.baseline_threshold_units = baseline_threshold
    alloc.target_threshold_units = target_threshold
    alloc.initial_valuation_units = unit_sum
    return alloc


def compute_markov_profile(
    w_patterns: Dict[str, float],
    target: Union[str, int],
    copies_or_max_rune: Union[int, str] = 1,
    min_cube_rune: str = "Pul",
    chests_per_run: int = 6,
    total_patterns: int = TOTAL_PATTERNS
) -> Tuple[np.ndarray, np.ndarray, Dict[int, float], int]:
    """
    Solve the absorbing Markov chain for all states i in {0, ..., W}.
    Accepts either:
      compute_markov_profile(w_patterns, 'Ber', 2) -> 2x Ber (W = 1024)
      or direct threshold:
      compute_markov_profile(w_patterns, 768, 'Ber') -> W = 768 units, max drop Ber
    Returns (E_runs, E_runs_sq, run_probs, W).
    """
    idx_min = RUNE_ORDER.index(min_cube_rune)

    if isinstance(target, int):
        W = target
        max_rune = copies_or_max_rune if isinstance(copies_or_max_rune, str) else "Ber"
        idx_target = RUNE_ORDER.index(max_rune)
    else:
        headliner = target
        headliner_copies = copies_or_max_rune if isinstance(copies_or_max_rune, int) else 1
        idx_target = RUNE_ORDER.index(headliner)
        K = idx_target - idx_min
        W = headliner_copies * (1 << K)

    # Single chest transition step distribution
    step_probs: Dict[int, float] = {}
    p_useful = 0.0
    for idx in range(idx_min, idx_target + 1):
        r = RUNE_ORDER[idx]
        val = 1 << (idx - idx_min)
        p_r = w_patterns[r] / total_patterns
        step_probs[val] = step_probs.get(val, 0.0) + p_r
        p_useful += p_r
    step_probs[0] = 1.0 - p_useful

    # 6-chest run convolution (capped at W)
    run_probs = {0: 1.0}
    for _ in range(chests_per_run):
        new_probs: Dict[int, float] = {}
        for v1, p1 in run_probs.items():
            for v2, p2 in step_probs.items():
                v_sum = min(W, v1 + v2)
                new_probs[v_sum] = new_probs.get(v_sum, 0.0) + p1 * p2
        run_probs = new_probs

    # Back-substitution on upper-triangular system
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

    return E_runs, E_runs_sq, run_probs, W


def compute_quantiles_from_state(
    run_probs: Dict[int, float],
    W: int,
    initial_state: int,
    chests_per_run: int = 6,
    max_runs: int = 25000
) -> Quantiles:
    """
    Evolve state distribution vector starting with mass 1.0 at initial_state
    to obtain exact quantiles: 50% (median), 75%, 90%, 95%, 99%.
    """
    if initial_state >= W:
        return Quantiles(0, 0, 0, 0, 0)

    # Use run-level probabilities for fast O(max_runs * non_zero_jumps) evolution
    jumps = [(v, pv) for v, pv in run_probs.items() if v > 0]
    p0 = run_probs[0]

    state = np.zeros(W + 1)
    state[initial_state] = 1.0

    targets = [0.50, 0.75, 0.90, 0.95, 0.99]
    found = {}

    for r in range(1, max_runs + 1):
        new_transient = p0 * state[0:W]
        for v, pv in jumps:
            if W - v > 0:
                new_transient[v:W] += pv * state[0:W - v]
        prob_absorbed = max(state[W], 1.0 - float(np.sum(new_transient)))
        state[0:W] = new_transient
        state[W] = prob_absorbed

        for q in targets:
            if q not in found and prob_absorbed >= q:
                found[q] = r

        if len(found) == len(targets):
            break

    return Quantiles(
        p50_median=found.get(0.50, max_runs),
        p75=found.get(0.75, max_runs),
        p90=found.get(0.90, max_runs),
        p95=found.get(0.95, max_runs),
        p99=found.get(0.99, max_runs),
    )


def compute_collateral_support_drops(
    missing_support: Dict[str, int],
    expected_runs: float,
    w_patterns: Dict[str, float],
    chests_per_run: int = 6,
    total_patterns: int = TOTAL_PATTERNS
) -> List[CollateralExpectation]:
    """Calculate expected natural drops of missing support runes during the remaining runs."""
    results = []
    total_chests = expected_runs * chests_per_run
    for rune, needed in missing_support.items():
        if rune in w_patterns:
            p_chest = w_patterns[rune] / total_patterns
            expected_drops = total_chests * p_chest
            
            # Poisson approximation for >= needed: 1 - sum_{k=0}^{needed-1} e^(-lambda) lambda^k / k!
            lam = expected_drops
            prob_at_least = 1.0
            term = math.exp(-min(700.0, lam))
            sum_prob = 0.0
            for k in range(needed):
                if k > 0:
                    term *= lam / k
                sum_prob += term
            prob_at_least = max(0.0, 1.0 - sum_prob)
            
            results.append(CollateralExpectation(
                rune=rune,
                needed=needed,
                expected_drops=expected_drops,
                prob_at_least_needed=prob_at_least
            ))
    return results


def analyze_stash_for_target(
    target: str,
    current_stash: Optional[Dict[str, int]] = None,
    player_setting: str = "p7",
    min_cube_rune: str = "Pul",
    chests_per_run: int = 6,
    p_lock: float = DEFAULT_P_LOCK
) -> AnalysisResult:
    """
    Main user-facing analysis function.
    """
    if current_stash is None:
        current_stash = {}

    target_name, recipe_runes, support_runes, _, recipe_text, target_type = resolve_target(target)

    alloc = allocate_stash(
        target_name=target_name,
        recipe_runes=recipe_runes,
        support_runes=support_runes,
        current_stash=current_stash,
        min_cube_rune=min_cube_rune
    )

    table = PATTERNS_TABLES.get(player_setting.lower(), PATTERNS_TABLES["p7"])
    w_patterns = weighted_patterns(table, p_lock)

    # 1. Baseline profile from scratch:
    W_baseline = alloc.baseline_threshold_units
    E_base, _, _, _ = compute_markov_profile(
        w_patterns=w_patterns,
        target=W_baseline,
        copies_or_max_rune=alloc.max_useful_rune,
        min_cube_rune=min_cube_rune,
        chests_per_run=chests_per_run,
        total_patterns=TOTAL_PATTERNS
    )
    baseline_expected = float(E_base[0])

    # 2. Remaining profile based on reserved sockets and surplus cubing value:
    W_remaining = alloc.target_threshold_units

    if W_remaining <= 0:
        expected = 0.0
        sd = 0.0
        runs_saved = baseline_expected
        pct_prog = 100.0
        quants = Quantiles(0, 0, 0, 0, 0)
    else:
        E_runs, E_runs_sq, run_probs, W = compute_markov_profile(
            w_patterns=w_patterns,
            target=W_remaining,
            copies_or_max_rune=alloc.max_useful_rune,
            min_cube_rune=min_cube_rune,
            chests_per_run=chests_per_run,
            total_patterns=TOTAL_PATTERNS
        )
        init_state = min(W, alloc.initial_valuation_units)
        if init_state >= W:
            expected = 0.0
            sd = 0.0
            runs_saved = baseline_expected
            pct_prog = 100.0
            quants = Quantiles(0, 0, 0, 0, 0)
        else:
            expected = float(E_runs[init_state])
            var = max(0.0, float(E_runs_sq[init_state] - expected ** 2))
            sd = math.sqrt(var)
            runs_saved = max(0.0, baseline_expected - expected)
            pct_prog = max(0.0, min(100.0, (runs_saved / baseline_expected * 100.0))) if baseline_expected > 0 else 100.0
            quants = compute_quantiles_from_state(run_probs, W, init_state, chests_per_run)

    times = TimeEstimates(
        hours_20s=(expected * 20.0) / 3600.0,
        hours_25s=(expected * 25.0) / 3600.0,
        hours_30s=(expected * 30.0) / 3600.0,
    )

    collateral = compute_collateral_support_drops(
        missing_support=alloc.missing_support,
        expected_runs=expected,
        w_patterns=w_patterns,
        chests_per_run=chests_per_run
    )

    recipe_desc = recipe_text.split(" (")[0] if "(" in recipe_text else recipe_text

    return AnalysisResult(
        target_name=target_name,
        target_type=target_type,
        player_setting=player_setting,
        chests_per_run=chests_per_run,
        min_cube_rune=min_cube_rune,
        allocation=alloc,
        expected_runs=expected,
        std_dev_runs=sd,
        baseline_expected_runs=baseline_expected,
        runs_saved=runs_saved,
        pct_progress=pct_prog,
        quantiles=quants,
        times=times,
        collateral_drops=collateral,
        recipe_runes=recipe_desc
    )


def format_analysis_report(res: AnalysisResult) -> str:
    """Format an AnalysisResult into a beautiful, human-readable terminal report."""
    alloc = res.allocation
    lines = []
    lines.append("=" * 68)
    lines.append(f" LOWER KURAST SUPERCHEST MARKOV ANALYSIS ({res.player_setting.upper()})")
    lines.append("=" * 68)
    if res.recipe_runes:
        lines.append(f"Target:           {res.target_name} ({res.recipe_runes})")
    elif res.target_type == "runeword":
        lines.append(f"Target:           {res.target_name} (RUNEWORD)")
    else:
        lines.append(f"Target:           {res.target_name} (RUNE)")

    target_summary = " + ".join(f"{cnt}x {r}" if cnt > 1 else r for r, cnt in alloc.recipe_runes.items())
    lines.append(f"Recipe Goal:      {target_summary} (Baseline Threshold W = {alloc.baseline_threshold_units} {res.min_cube_rune} units)")
    lines.append(f"Min Cubing Tier:  {res.min_cube_rune}+ (Binary 2-to-1 lattice)")
    lines.append("-" * 68)
    
    lines.append("STASH INVENTORY ALLOCATION:")
    if alloc.reserved_recipe:
        res_rec_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.reserved_recipe.items())
        lines.append(f"  [+] Recipe Slots Reserved:    {res_rec_str}  [OK]")
    if alloc.missing_recipe:
        mis_rec_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.missing_recipe.items())
        lines.append(f"  [-] Missing Recipe Runes:     {mis_rec_str} (Remaining W = {alloc.target_threshold_units} {res.min_cube_rune} units)")
    if alloc.reserved_support:
        res_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.reserved_support.items())
        lines.append(f"  [+] Support Slots Reserved:   {res_str}  [OK]")
    if alloc.missing_support:
        mis_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.missing_support.items())
        lines.append(f"  [-] Missing Support Slots:    {mis_str}")
    if alloc.surplus_runes_for_cubing:
        sur_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.surplus_runes_for_cubing.items())
        lines.append(f"  [>] Applied to Cubing Ladder: {sur_str}")
        pct_surplus = (alloc.initial_valuation_units / alloc.target_threshold_units * 100.0) if alloc.target_threshold_units > 0 else 100.0
        lines.append(f"      Accumulated Starting Valuation: {alloc.initial_valuation_units} / {alloc.target_threshold_units} {res.min_cube_rune} units ({pct_surplus:.1f}%)")
    else:
        lines.append("  [>] Applied to Cubing Ladder: None (Starting from scratch: 0 units)")
    
    if alloc.unusable_higher_runes:
        un_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.unusable_higher_runes.items())
        lines.append(f"  [*] Higher Runes Preserved:   {un_str} (Cannot cube downward; kept in stash)")
    if alloc.sub_min_runes:
        sub_str = ", ".join(f"{cnt}x {r}" for r, cnt in alloc.sub_min_runes.items())
        lines.append(f"  [i] Sub-Ladder Runes:         {sub_str} (Sub-{res.min_cube_rune})")

    lines.append("-" * 68)
    lines.append("REMAINING RUNS TO GOAL:")
    if alloc.target_threshold_units <= 0 or (alloc.surplus_runes_for_cubing and alloc.initial_valuation_units >= alloc.target_threshold_units):
        lines.append("  GOAL ALREADY MET! Your stash already contains enough runes to complete this target!")
        lines.append(f"  Runs saved: {res.runs_saved:.1f} runs (100% complete)")
    else:
        lines.append(f"  Expected Runs E[R | stash]:   {res.expected_runs:7.1f} runs (Baseline from scratch: {res.baseline_expected_runs:.1f})")
        lines.append(f"  Standard Deviation SD[R]:     {res.std_dev_runs:7.1f} runs")
        lines.append(f"  Grind Completed by Stash:     {res.runs_saved:7.1f} runs saved ({res.pct_progress:.1f}% progress)")
        lines.append(f"  Estimated Farming Time:       {res.times.hours_25s:.1f} hrs @ 25s/run ({res.times.hours_20s:.1f} hrs @ 20s, {res.times.hours_30s:.1f} hrs @ 30s)")

    lines.append("-" * 68)
    lines.append("DISTRIBUTION OF WAITING TIMES (TAIL RISKS):")
    lines.append(f"  50% Median Wait:              {res.quantiles.p50_median:6d} runs")
    lines.append(f"  75th Percentile:              {res.quantiles.p75:6d} runs")
    lines.append(f"  90th Percentile Drought:      {res.quantiles.p90:6d} runs (1 in 10 players take this long)")
    lines.append(f"  95th Percentile Drought:      {res.quantiles.p95:6d} runs (1 in 20 players take this long)")
    lines.append(f"  99th Percentile Tail Risk:    {res.quantiles.p99:6d} runs (1 in 100 players take this long)")

    if res.collateral_drops:
        lines.append("-" * 68)
        lines.append("COLLATERAL MID-RUNE HARVEST DURING HEADLINER GRIND:")
        for col in res.collateral_drops:
            lines.append(
                f"  {col.rune} Slot (need {col.needed}x): Expected {col.expected_drops:.2f} direct drops "
                f"({col.prob_at_least_needed * 100:.1f}% chance of naturally completing the slot in LK)"
            )
        lines.append("  TIP: If missing lower slots, Countess on /players 1 fills Mal/Ist in ~15-30 min!")

    lines.append("=" * 68)
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    # Quick demo if run directly
    sample_stash = {"Ist": 1, "Gul": 1, "Pul": 2}
    print("DEMO: Target = 'Call to Arms' with Stash = {'Ist': 1, 'Gul': 1, 'Pul': 2}")
    result = analyze_stash_for_target("Call to Arms", sample_stash, "p7")
    print(format_analysis_report(result))
