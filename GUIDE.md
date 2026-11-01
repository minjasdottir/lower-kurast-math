# Reasonable Expectations in Lower Kurast: A Field Guide

Offline single-player Lower Kurast is a long grind and mentally challenging to endure no matter how you slice it. Make the best of it by optimizing your map up front, cutting out distractions, and avoiding folklore pitfalls. This guide provides **new and improved expected run** numbers based on exact chest patterns (including lock mechanics) reverse-engineered by Fruit, verified by fearedbliss, informed by Nefarius's classic data file guides, and modeled using absorbing Markov chains.

---

## How Long You Must Grind

**Here are your expected runs and actual gameplay hours.** I assume you are using a Sorceress on an optimal 6-chest Lower Kurast map.

If you really want the math, read *Stop "Doing Random Shit" in Lower Kurast: Keeping your Superstition at Bay (Sister Eir)*. It contains the explanations of absorbing Markov chains based on the exact rune patterns found in unpacked game files and disassembly analysis around the impact of locked and unlocked chests.

### Table 1: Major Endgame Runewords

| Target Runeword | Expected Runs | Approx. Time @ 20s (God Map) | Approx. Time @ 25s (Good Map) | Direct Drop Only (No Cubing) | Naive Estimate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Heart of the Oak** | **862 runs** | 4.8 hrs | 6.0 hrs | 1,821 runs | 693 runs (-24%) |
| **Call to Arms** | **1,058 runs** | 5.9 hrs | 7.3 hrs | 2,185 runs | 848 runs (-25%) |
| **Grief / Fortitude** | **1,570 runs** | 8.7 hrs | 10.9 hrs | 5,462 runs | 1,294 runs (-21%) |
| **Infinity** | **2,865 runs** | 15.9 hrs | 19.9 hrs | 10,923 runs (2×Ber) | 2,537 runs (-13%) |
| **Enigma** | **4,136 runs** | 23.0 hrs | 28.7 hrs | *N/A (Jah cannot drop in LK)* | 3,806 runs (-9%) |

> [!TIP]
> **Enigma Hunters:** Lower Kurast superchests cap at `Ber` and **cannot drop Jah directly**. Therefore, your Enigma requires cubing two Bers into a Jah. Overall, you need 3 Ber runes.  
> **Kill The Countess For Stray Mid Runes:** Dropping an early Ohm before finding Mal + Ist for a *Call to Arms* means waiting for the dedicated lower slots if farming strictly in LK (increasing exact multi-slot expectation for *Call to Arms* to **1,521 runs**, and *Grief*'s Lo + Mal to **1,670 runs**). Visiting the Hell Countess on `/players 1` easily fills these mid-rune slots. Don't grind Lower Kurast for Pul if you already have your Vex for Heart of the Oak, for example.

### Table 2: Individual Mid & High Runes (Mal–Ber)

| Target Rune | Expected Runs | Approx. Time @ 20s (God Map) | Approx. Time @ 25s (Good Map) | Direct Drop Only (No Cubing) | Naive Estimate (Overshoot) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Mal (#23)** | **559 runs** | 3.1 hrs | 3.9 hrs | 770 runs | 469 runs (-16%) |
| **Ist (#24)** | **768 runs** | 4.3 hrs | 5.3 hrs | 2,023 runs | 641 runs (-17%) |
| **Gul (#25)** | **699 runs** | 3.9 hrs | 4.9 hrs | 993 runs | 559 runs (-20%) |
| **Vex (#26)** | **862 runs** | 4.8 hrs | 6.0 hrs | 1,821 runs | 693 runs (-24%) |
| **Ohm (#27)** | **1,058 runs** | 5.9 hrs | 7.3 hrs | 2,185 runs | 848 runs (-25%) |
| **Lo (#28)**  | **1,570 runs** | 8.7 hrs | 10.9 hrs | 5,462 runs | 1,294 runs (-21%) |
| **Sur (#29)** | **1,037 runs** | 5.8 hrs | 7.2 hrs | 1,214 runs | 826 runs (-26%) |
| **Ber (#30)** | **1,558 runs** | 8.7 hrs | 10.8 hrs | 5,462 runs | 1,269 runs (-23%) |

> [!IMPORTANT]
> **Boundary Overshoot Penalty and the Naive Weighted-Drift Estimate Oversimplification:**  
> Traditional community calculators divide 1.0 target rune by the average fractional rune value dropped per run, estimating that Ber takes 1,269 runs. While useful as a first-order benchmark, this linear-drift approximation underestimates individual rune grinds by **21% to 26% (+290 runs on Ber)** because it does not account for the "leftover change" in your stash when a direct rune drops. If you have 7/8 of a Lo rune in your stash and a natural Lo drops, that accumulated stash value does not speed up your first Lo (though it rolls over toward your next runeword, which is why the difference shrinks from +23% on a single Ber to +8.7% on *Enigma*).

---

## You Must Take Time Rolling a Map

Because Lower Kurast involves hundreds or thousands of repetitive runs, **your map layout is the single biggest determinant of your real-world farming speed.** How long does it take to roll a good one, and why does it matter?

### Map Categories

Lower Kurast maps fall into four distinct tiers:

| Map Tier | Description | Frequency | Avg. Run Time | Status / Action |
| :--- | :--- | :---: | :---: | :--- |
| **Perfect (Circular)** | Waypoint sits directly between or adjacent to both campfires. Movement forms a seamless, uninterrupted loop (WP → CF 1 → CF 2 → WP → Act IV) with zero backtracking. | **≈ 7%** (1 in 14 rolls) | **18–22 s** | **The Gold Standard.** Lock this map in and never switch difficulties again. |
| **Mediocre Linear Split** | Both campfires are in the same general half of LK, but arranged in a line away from the waypoint (WP → CF 1 → CF 2), requiring backtracking or a long exit path. | **≈ 21%** (1 in 4.8 rolls) | **25–28 s** | **Usable for short goals.** Fine for *HOTO*, but costs multiple extra hours on long grinds. |
| **6-Chest "Split" Map** | Both campfires exist, but they are on opposite sides of the zone, separated by rivers, dead ends, or bridges. | **≈ 22%** (1 in 4.5 rolls) | **33–40 s** | **Discard.** Travel time between campfires adds 10s+ of dead teleporting every run. |
| **Trash** | Only 1 campfire preset placed by DRLG (3 superchests total). | **≈ 50%** (1 in 2 rolls) | N/A | **Instant Reroll.** Running this doubles your run requirements (8,272 runs for Enigma). |

---

### Rolling a Good Lower Kurast Map

Because your maps stay constant unless you switch difficulties *on that character*, you "roll" your map by switching between difficulties. Specifically:

1. Load your Hell character in Single Player.
2. Hit **Escape → Save & Exit**.
3. Change difficulty to **Nightmare** (or Normal) and enter the game.
4. Immediately **Save & Exit**.
5. Switch difficulty back to **Hell** and enter the game. This forces `D2Common.dll` to wipe the level seed and generate a brand-new Act III layout.
6. Take the Act III town waypoint directly to **Lower Kurast**.

#### The 5-Second Scouting Routine

Do **not** explore the entire Lower Kurast map on foot or tele-scout every corner:
- Teleport out from the waypoint in an immediate circular perimeter (roughly 2–3 screens out).
- Campfire bonfires appear on your automap as a distinct circular clearing surrounded by small wall silhouettes.
- If you do not see at least one campfire within 2–3 teleports of the waypoint, or if you locate one campfire but the rest of the zone is a dead-end swamp maze, **immediately Save & Exit and reroll**.

### Character Setup & The Act IV Reset Loop
To hit the sub-25s benchmarks:
- **Sorceress FCR Breakpoints:** Run at the **105% Faster Cast Rate (8-frame Teleport)** breakpoint, or at minimum **63% FCR** (9 frames). If you don't have those items yet on a fresh single-player account, you can moat-trick Hell Mephisto for core mid-level caster gear (*Skin of the Vipermagi*, *Magefist*, etc.).
- **The Act IV Town Reset Phase:** In Act III (Kurast Docks), characters cannot cast *Teleport* in town and spawn far down on the docks, forcing a long walk to the waypoint (at best expedited with a *Harmony* bow's Vigor aura) before *Telekinesis* can reach it. Instead, execute an **Act IV reset phase**: on a circular map (WP → CF 1 → CF 2 → WP), end your run by clicking the LK Waypoint, traveling to **Act IV (The Pandemonium Fortress)**, and Saving & Exiting there. In Act IV, you spawn directly next to the Waypoint, allowing you to instantly cast *Telekinesis* on the waypoint with zero walking and jump straight back into LK!
- **Key Reserve:** Because roughly 1 in 5 superchests spawns locked, keep a dedicated $4 \times 3$ block of keys in your inventory (12 stacks = $144\text{ keys}$, bought from Halbu or Jamella in Act IV). This covers $\approx 120\text{ runs}$ without interrupting your farming rhythm. Skipping locked chests forfeits 20% of your drop capacity!

#### Map Optimization Caveat: Weapon & Armor Racks (Seed-Locked Base Harvesting)

A consideration for you might be weapon and armor racks, and you might hit a map that, while being mediocre, drops a base that you need, such as **Thresher** or **Cryptic Axe** (for *Infinity* or *Insight*), **Mancatcher** (*Infinity* only), **Phase Blades** (for *Grief*), and **Mage Plates** / **Dusk Shrouds** (for *Enigma*). In that case, it might be reasonable to keep the map.

Because Lower Kurast is Area Level 80, racks drop up to $\text{qlvl } 79$ ($\text{ilvl} = \text{alvl} - 1$). This means Threshers ($\text{qlvl } 71$) *can* drop, but higher-qlvl bases like **Giant Threshers** ($\text{qlvl } 86$), **Colossus Swords** ($\text{qlvl } 80$), and **Archon Plates** ($\text{qlvl } 84$) cannot drop unless terrorized. The deeper mechanics of seed-locked rack farming are beyond the scope of this guide.

#### Balancing Reroll Time Against Your Farming Goal

Rerolling an Act III map in D2R takes approximately **25 seconds** per attempt (menu toggle, loading screen, waypoint, quick scout). 
- Finding **any** 6-chest map takes ≈ 2 attempts (≈ 1 minute).
- Finding a **Tier 2 Linear** map takes ≈ 5 attempts (≈ 2.5 minutes).
- Finding a **Tier 3 God-Roll Loop** takes ≈ 14 attempts (≈ 6–8 minutes; 90th percentile worst-case is ≈ 32 attempts or 15 minutes).

### Why Good Maps Matter

How much does settling for a mediocre map actually cost you in wasted gameplay?

| Target Goal | Expected Runs | Hours @ 20s (God Map) | Hours @ 26s (Linear Map) | Hours @ 35s (Split Map) | Time Lost by Settling for Linear Map |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Heart of the Oak (Vex)** | 862 | 4.8 hrs | 6.2 hrs | 8.4 hrs | **+1.4 hours** (+84 min) |
| **Call to Arms (Ohm)** | 1,058 | 5.9 hrs | 7.6 hrs | 10.3 hrs | **+1.8 hours** (+106 min) |
| **Grief / Fortitude (Lo)** | 1,570 | 8.7 hrs | 11.3 hrs | 15.3 hrs | **+2.6 hours** (+157 min) |
| **Infinity (2×Ber)** | 2,865 | 15.9 hrs | 20.7 hrs | 27.9 hrs | **+4.8 hours** (+287 min) |
| **Enigma (3×Ber)** | 4,136 | 23.0 hrs | 29.9 hrs | 40.2 hrs | **+6.9 hours** (+414 min) |

### The Pragmatic Rule of Thumb
- **Farming only a Vex (*HOTO*)?** A Tier 2 linear map (25–26s) is acceptable if you are impatient, though spending 8 minutes rolling a God Map still repays itself **tenfold** (+84 minutes saved).
- **Farming *Grief*, *Infinity*, or *Enigma*?** **Never settle.** Settling for a mediocre map burns between **2.6 and 6.9 extra hours** of mindless clicking. Settling for a bad split map burns **over 17 hours**. Spend the 10–15 minutes upfront to roll a tight circular loop.

---

## Avoid Folklore Pitfalls

Do not fall prey to misinformation that will waste your time. Proofs are in the paper, so I only mention them here briefly.

### Always and Forever `/players 7`

**Never run `/players 5` under any circumstances.**

#### The Lo Rune Myth

There is a persistent myth that if you're hunting a Lo rune, you might consider `/players 5`. Don't fall for that. Smart runners don't wait for a natural Lo to drop—they cube up to it. **Over 76% of your progress toward a Lo rune comes from cubing Ohm, Vex, and Gul drops**:
- `/players 7` drops **2.5× more Ohm runes** (5 patterns vs. 2) and **2.2× more Gul runes** (11 patterns vs. 5).
- Consequently, cubing toward a Lo takes **1,570 runs on `/players 7` vs. 1,714 runs on `/players 5`** (**144 runs faster**).
- `/players 7` also drops **+66.7% more Sur runes** (9.0 patterns vs. 5.4) and **+12.1% more total High Runes**.

> [!TIP]
> **The Core Law of Lower Kurast:**  
> **"Ber and Lo don’t get you Ber and Lo. Gul and Ohm get you Lo. Sur gets you Ber."**  
> Direct Lo and Ber drops are 1 in 5,462-run longshots. You build endgame runewords using the workhorse drops that `/players 7` showers you with: **Sur** (1 in 1,214), **Gul** (1 in 993), and **Ohm** (1 in 2,185).

#### It's not Just Lo Rune: `/players 7` Beats `/players 5` for Every Rune (Mal–Ber)

`/players 7` strictly beats `/players 5` for **every single rune from Mal (#23) through Ber (#30)**:
- **Mal (#23):** 559 runs on `/p7` vs. 663 on `/p5` (**15.6% faster**; +42% more drops)
- **Ist (#24):** 768 runs on `/p7` vs. 877 on `/p5` (**12.4% faster**)
- **Gul (#25):** 699 runs on `/p7` vs. 1,076 on `/p5` (**35.1% faster**; +120% more drops)
- **Vex (#26):** 862 runs on `/p7` vs. 1,121 on `/p5` (**23.2% faster**)
- **Ohm (#27):** 1,058 runs on `/p7` vs. 1,641 on `/p5` (**35.5% faster**; +150% more drops)
- **Lo (#28):** 1,570 runs on `/p7` vs. 1,714 on `/p5` (**8.4% faster**)
- **Sur (#29):** 1,037 runs on `/p7` vs. 1,464 on `/p5` (**29.2% faster**; +67% more drops)
- **Ber (#30):** 1,558 runs on `/p7` vs. 1,577 on `/p5` (**1.2% faster**)

*(For the complete mathematical debunking of community `/players 5` simulations and streamer case studies, see Section 6 of the companion paper.)*

*What about Pul and Um?* While `/players 5` has a negligible 34-run edge on Um, farming LK for mid-runes is a massive blunder: the Hell Countess on `/players 1` drops direct Pul/Um at 1 in 78 runs (and cubes up every 14–28 runs), whereas LK requires ~670 runs.


### Don't "Do Random Shit"

Your pathing cannot ever be "too precise." Varying your path or hitting poppables does nothing for the RNG. Lower Kurast's superchests are six `65534`-card decks. Every single second you spend wandering around kicking logs or flipping corpses is simply drawing from a terrible junk deck while burning the clock. That Ber rune is just as likely to drop whether or not Doom Apes were blocking your Telekinesis click.

### Don't Pick Up Every Gem and Charm

Many runners fall into the trap of picking up Flawless Gems, checking rare rings and amulets, or hoarding low runes:
- Base run time on a good map: **25 seconds**.
- Picking up an average of 2.5 collateral items per run costs an amortized **4 seconds per item** (walking back into huts, inventory tetris, town trips, and cube transmuting).
- **Result:** +10 seconds per run (run time increases from 25s to 35s).

> [!WARNING]
> That 10-second pickup penalty **slashes your High Rune arrival rate by 28.6%**. Over a 4,136-run *Enigma* grind, collateral looting adds **11.5 hours of pure inventory chores**—equivalent to throwing away **1,654 chest runs** or **3.6 expected High Runes**!

**Use a strict loot filter** to hide clutter, prevent misreading low runes (*Io* for *Lo*, *Sol* for *Sur*), and bypass the client's **32-item display ceiling** so high runes are never hidden off-screen.

---

## Psychological Reality

It is incredibly frustrating to run Lower Kurast hundreds and hundreds of times and feel like you're "running dry." Mathematically, you cannot run dry forever. But equally true, mathematically, you *will* run very, very dry *sometime*.

### Droughts are Normal and Expected

Across thousands of Diablo II players, the following will happen.

- If we each farm 15 high runes, then **1 in 6 of us (17.0%)** will endure a drought of **2,000+ consecutive runs** without a single High Rune.
- On `/players 7`, the probability of finding **any** High Rune (Vex, Ohm, Lo, Sur, Ber) in a 6-chest run is 1 in 455.5 runs (0.22%).
- `D2Game.dll` has no memory. If you have gone 2,000 runs without a drop, your expected runs to the next High Rune is **still exactly 455.5 runs**.

### Stay Healthy and Stay the Course

Don't make a 2,500-run drought worse by varying your pathing and taking 40 seconds a run thinking your luck is "due" to turn around. Run efficiently, trust the law of large numbers. Take walking breaks, listen to music, and care for your friends and family along the way.

## Summary

The golden rules of Lower Kurast running are:

1. **Roll a Sub-22s Circular Loop:** Spend 10–15 minutes securing a map where both campfires loop smoothly back to the waypoint (`WP → CF 1 → CF 2 → WP → Act IV`).
2. **Always Run `/players 7`:** Never drop to `/p5` or `/p3`, and never run `/p8` (same loot as `/p7`, but +50% monster HP).
3. **Practice "Lazy" (Just-in-Time) Cubing:** Keep Pul through Vex uncubed until you reach your goal. Passively maintain "minimum gem diversity" by stashing lower-grade gems during Normal and Nightmare playthroughs so you have Flawed Amethysts ready for $2\text{ Sur} \to \text{Ber}$.
4. **Never Cube Lo Runes Upward:** Natural Lo drops are rare (2 patterns on `/p7`) and essential for *Grief* and *Fortitude*. Withholding Lo delays *Infinity* by only 191 runs—a trivial price to retain physical endgame gear.
5. **Ignore the Clutter:** Pop the 6 chests, snatch orange Pul+ labels, take the waypoint to Act IV, and reset.

---

## References & Credits

- **Companion Academic Paper:** Sister Eir, *Stop "Doing Random Shit" in Lower Kurast: Keeping Your Superstition at Bay* (companion manuscript containing full Markov transition matrices, PRNG disassembly proofs, and `/players 5` simulation critiques).
- **Reverse Engineering & Drop Emulation:** **Fruit** (`d2pg` pattern generator).
- **Archival Verification & Environment Isolation:** **fearedbliss** (*Cactus* version manager).
- **Data File Specifications & Engine Mechanics:** **Nefarius** (*The Phrozen Keep* file guides).
- **Community Reference & Drop Tables:** **TheHappyDev** (*d2runes.io*).
- **Theoretical Foundation:** J. G. Kemeny & J. L. Snell (*Finite Markov Chains*, 1960) and W. Feller (*An Introduction to Probability Theory and Its Applications*, 1968).
