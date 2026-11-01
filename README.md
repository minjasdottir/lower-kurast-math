# Lower Kurast Run Planner

## Features

Estimate your grind for specific runes or runewords in single-player Hell Lower Kurast!

- **Expected runs of major runewords**: not just Enigma/Infinity
- **Dry spells**: 90th, 95th, 99th percentiles
- **Math accounts for rune cubing exactly**: Pul-Ber

> [!NOTE]
> This tool does not analyze Last Wish or the Cham/Zod runewords. You can farm them in Lower Kurast, for sufficiently optimistic definitions of "can". Oof.

## Math Improvements

This tool applies math in a new way to improve on existing community estimates of expected runs and variance.

- **Discrete Absorbing Markov chains**: Read [the paper](<paper/Stop Doing Random Shit in Lower Kurast.pdf>) if you are curious.
- **No Monte Carlo used**: We don't compute millions of simulated drops.
- **No weighted-drift estimation**: Absorbing Markov chains allow us to be exact.
- **Gold-standard weighted locked/unlocked chest patterns applied**: TheHappyDev's d2runes.io shows accurate chest patterns from reverse engineering of Fruit/bonqen, verified by fearedbliss.

---

## 1. Quickstart & Usage

The planner is located in [`code/lk_run_planner.py`](code/lk_run_planner.py) (backed by the engine in [`code/lk_generalized_rune_cubing.py`](code/lk_generalized_rune_cubing.py)).

### Mode A: Interactive Guided Menu
Launch the interactive planner directly from your terminal:
```bash
python3 code/lk_run_planner.py
```
You will be prompted through:
1. **Target Selection:** Choose from 16 popular progression runewords, individual high runes, or a custom target.
2. **Player Count:** Select `/players 7-8` (recommended) or `/players 5-6` (to test and verify why it is suboptimal).
3. **Stash Inventory:** Enter your current runes (e.g., `1 Ist, 1 Gul, 2 Pul` or `Ist: 1, Gul: 1`), type `guided` for step-by-step entry, or press **Enter** for an empty stash (starting from scratch).

### Mode B: Direct CLI Flags (Fast & Scriptable)
Run one-off scenarios instantly using shell arguments:
```bash
# Call to Arms with 1 Ist and 1 Gul in stash:
python3 code/lk_run_planner.py --target "Call to Arms" --stash "Ist: 1, Gul: 1" --players p7

# Infinity with 1 Sur in stash:
python3 code/lk_run_planner.py --target "Infinity" --stash "Sur: 1"

# Heart of the Oak with 2 Puls:
python3 code/lk_run_planner.py --target "Heart of the Oak" --stash "Pul: 2"

# Direct Ber Rune on /players 7 vs /players 5:
python3 code/lk_run_planner.py --target "Ber" --players p7
python3 code/lk_run_planner.py --target "Ber" --players p5
```

### Mode C: Python Library API
Use the Markov solver directly inside your own Python scripts:
```python
import lk_generalized_rune_cubing as lk_gen

# Analyze stash for Call to Arms on /players 7
result = lk_gen.analyze_stash_for_target(
    target="Call to Arms",
    current_stash={"Ist": 1, "Gul": 1, "Pul": 2},
    player_setting="p7"
)

# Print the terminal report
print(lk_gen.format_analysis_report(result))

# Or access raw numerical values directly
print(f"Remaining expected runs: {result.expected_runs:.1f}")
print(f"Standard deviation:     {result.std_dev_runs:.1f}")
print(f"50% Median wait:        {result.quantiles.p50_median} runs")
print(f"90th percentile drought:{result.quantiles.p90} runs")
```

---

## 2. Example Simulations

### Socket Reservation vs. Cubing Ladder (*Faith*)

Starting from scratch, *Faith* (`Ohm + Jah + Lem + Eld`) requires Jah (1,024 Pul-units) plus Ohm (64 Pul-units), totaling 1,088 Pul-units (**3,021.6 runs**). 

* **Starting with 1 Ohm:**
  When you supply 1 Ohm, the tool reserves that Ohm for the weapon socket:
  ```text
  [+] Recipe Slots Reserved:    1x Ohm  [OK]
  [-] Missing Recipe Runes:     2x Ber (Remaining W = 1024 Pul units)
  ```
  That Ohm is **reserved for the Bow**, not burned in the Horadric Cube! You now only need the Jah grind (2 Ber = 1,024 Pul units), dropping your expected runs to **2,865.3 runs** (**156.3 runs saved**).
* **Starting with a 2nd Ohm (`Ohm: 2`):**
  The first Ohm satisfies the socket, and the second Ohm enters the cubing ladder toward Jah (+64 Pul-units). Expected runs immediately drop from 2,865.3 to **2,714.6 runs** (**an additional 150.7 runs saved**)!

### `/players 5` Is Irrational (*Ice* Case Study)

If ever there were a case for `/players 5`, the *Ice* runeword should be that case. It requires `Jah + Lo` (1,152 Pul units: 2 Ber + 1 Lo in LK). This is the single strongest hypothetical scenario for `/players 5` advocates, because `/players 5` boasts **4 direct Lo patterns** and **4 direct Ber patterns** (versus only 2 of each on `/players 7`).

* **The Reality:** Even on *Ice*, **`/players 7` strictly dominates across both the mean and the tail**:
  * **Expected Runs:** **3,183.4 runs** on `/p7` vs. **3,227.2 runs** on `/p5`.
  * **50% Median Wait:** **2,998 runs** on `/p7` vs. **2,999 runs** on `/p5`.
  * **90th Percentile Drought:** **5,104 runs** on `/p7` vs. **5,378 runs** on `/p5` (**+274 extra runs** of tail drought on `/p5`!).
  * **99th Percentile Tail Risk:** **7,235 runs** on `/p7` vs. **7,868 runs** on `/p5` (**+633 extra runs** on `/p5`!).
* **Why `/players 7` Wins:** 
  Lower Kurast is an **assembly line, not a direct-drop lottery**. 
  To get a Ber, you need **Sur runes** (9.0 patterns on `/p7` vs 5.4 on `/p5`—a **+66.7% advantage**). 
  To get a Lo, you need **Ohm runes** (5.0 patterns on `/p7` vs 2.0 on `/p5`—a **+150% advantage**). 
  Starving your assembly line of Sur and Ohm drops on `/players 5` more than cancels out the direct drop rate, leaving you with higher variance and deeper dry spells.

### Basic Probability Reasoning: Mean `!=` Median

On `/players 7` from scratch, *Enigma* has an **Expected Run Count (Mean) of `4,136.4`**, but the **50% Median Wait is only `3,956` runs**.
* **Why this happens:**
  In everyday language, "expected" sounds like "the typical outcome." In mathematics, **Expected Value is strictly the arithmetic average (Mean)** across all possible timelines.
  * Drop waiting times are **positively (right) skewed**. The left side has a hard floor at 0 runs (you can never take negative runs), but the right side stretches out into severe droughts (6,320 runs at the 90th percentile; 8,676 runs at the 99th percentile).
  * Those extreme drought cases pull the arithmetic mean up to 4,136.4 runs.
  * The **Median (3,956 runs)** represents the true 50/50 mark: by run 3,956, **exactly 50% of players already have their Enigma**! By the time the arithmetic average (4,136 runs) is reached, roughly 54.4% of all players have already completed the runeword.

---

## 3. Summary Table: Baseline Expectations on `/players 7`

All runs assume optimized single-player farming (6 superchests per run, locked chest probability p = 0.20, cubing Pul+):

| Target | Recipe High Rune Goal | Expected Runs E[R] | Std Dev SD[R] | 50% Median | 90% Drought | Farming Time (25s/run) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mosaic** | 1x Gul + 1x Mal | 699.0 | 542.7 | 586 | 1,449 | 4.9 hours |
| **Heart of the Oak** | 1x Vex | 861.7 | 606.0 | 757 | 1,689 | 6.0 hours |
| **Call to Arms** | 1x Ohm | 1,057.8 | 717.6 | 950 | 2,035 | 7.3 hours |
| **Death** | 1x Vex + 1x Gul | 1,229.8 | 700.5 | 1,124 | 2,176 | 8.5 hours |
| **Beast** | 1x Ber | 1,558.0 | 1,035.0 | 1,387 | 2,969 | 10.8 hours |
| **Chains of Honor** | 1x Ber | 1,558.0 | 1,035.0 | 1,387 | 2,969 | 10.8 hours |
| **Grief** | 1x Lo | 1,569.9 | 928.9 | 1,461 | 2,820 | 10.9 hours |
| **Fortitude** | 1x Lo | 1,569.9 | 928.9 | 1,461 | 2,820 | 10.9 hours |
| **Eternity** | 1x Ber + 1x Sur | 2,222.3 | 1,205.3 | 2,062 | 3,840 | 15.4 hours |
| **Infinity** | 2x Ber | 2,865.3 | 1,359.3 | 2,699 | 4,684 | 19.9 hours |
| **Dream** | 2x Ber (Jah) | 2,865.3 | 1,359.3 | 2,699 | 4,684 | 19.9 hours |
| **Faith** | 2x Ber (Jah) + 1x Ohm | 3,021.6 | 1,395.3 | 2,845 | 4,896 | 21.0 hours |
| **Ice** | 2x Ber (Jah) + 1x Lo | 3,183.4 | 1,426.4 | 2,998 | 5,104 | 22.1 hours |
| **Brand** | 2x Ber (Jah) + 1x Lo + 1x Gul | 3,223.9 | 1,434.5 | 3,039 | 5,155 | 22.4 hours |
| **Phoenix** | 2x Ber (Jah) + 1x Lo + 2x Vex | 3,345.3 | 1,459.9 | 3,162 | 5,308 | 23.2 hours |
| **Enigma** | 3x Ber (Jah + Ber) | 4,136.4 | 1,632.7 | 3,956 | 6,320 | 28.7 hours |
