#!/usr/bin/env python3
"""
lk_run_planner.py
-----------------
Interactive companion tool and CLI for planning Lower Kurast superchest runs.
Powered by the exact absorbing Markov chain engine in lk_generalized_rune_cubing.py.

Usage:
  Interactive menu:
    $ python3 lk_run_planner.py

  Direct CLI flags:
    $ python3 lk_run_planner.py --target "Call to Arms" --stash "Ist:1,Gul:1,Pul:2" --players p7
    $ python3 lk_run_planner.py --target "Infinity" --stash "Sur:1,Lo:1"
    $ python3 lk_run_planner.py --target "Vex" --players p7
"""

import argparse
import sys
import re
from typing import Dict

import lk_generalized_rune_cubing as lk_gen


POPULAR_TARGETS = [
    ("Heart of the Oak", "Vex + Pul (HOTO caster weapon)"),
    ("Call to Arms", "Ohm + Ist + Mal (CTA pre-buff weapon)"),
    ("Grief", "Lo + Mal (BiS melee weapon)"),
    ("Fortitude", "Lo (BiS physical armor/weapon)"),
    ("Infinity", "2x Ber + Ist + Mal (Conviction polearm/spear)"),
    ("Enigma", "3x Ber equivalent (Jah + Ber armor in LK)"),
    ("Death", "Vex + Gul (Crushing Blow sword/axe)"),
    ("Faith", "2x Ber [Jah] + Ohm (Fanaticism bow)"),
    ("Beast", "Ber + Mal + Um (Fanaticism melee weapon)"),
    ("Phoenix", "2x Ber [Jah] + Lo + 2x Vex (Redemption shield)"),
    ("Dream", "2x Ber [Jah] + Pul (Holy Shock helm/shield)"),
    ("Ice", "2x Ber [Jah] + Lo (Holy Freeze bow)"),
    ("Brand", "2x Ber [Jah] + Lo + Gul + Mal (Bone Spear bow)"),
    ("Eternity", "Ber + Sur + Ist (Melee/Missile weapon)"),
    ("Mosaic", "Gul + Mal (Martial arts claw)"),
    ("Chains of Honor", "Ber + Ist + Um (All-res endgame armor)"),
    ("Vex Rune", "Direct Vex or cubing Pul->Vex"),
    ("Lo Rune", "Direct Lo or cubing Pul->Lo"),
    ("Sur Rune", "Direct Sur or cubing Pul->Sur"),
    ("Ber Rune", "Direct Ber or cubing Pul->Ber"),
    ("Custom Target", "Enter any rune(s) or runeword manually (e.g. 'Ber + Sur')"),
]


def parse_stash_string(text: str) -> Dict[str, int]:
    """
    Parse flexible stash strings like:
      'Ist: 1, Gul: 1, Pul: 2'
      '1 Ist, 1 Gul, 2 Pul'
      'Ist 1 Gul 1 Ber 2'
      'none' or '' -> {}
    """
    cleaned = text.strip()
    if not cleaned or cleaned.lower() in ["none", "empty", "0", "no", "n"]:
        return {}

    stash: Dict[str, int] = {}

    # Match patterns like 'Ist: 1' or 'Ist=1' or 'Ist 1' or '1 Ist' or '1x Ist'
    # Try comma / semicolon split first
    items = [x.strip() for x in re.split(r"[,;]+", cleaned) if x.strip()]
    if len(items) == 1 and " " in items[0] and ":" not in items[0] and "=" not in items[0]:
        # Might be space delimited: 'Ist 1 Gul 2'
        tokens = items[0].split()
        if len(tokens) >= 2 and len(tokens) % 2 == 0:
            # Pair them up
            i = 0
            while i < len(tokens):
                t1, t2 = tokens[i], tokens[i + 1]
                if t1.isdigit():
                    cnt, r = int(t1), t2.capitalize()
                elif t2.isdigit():
                    r, cnt = t1.capitalize(), int(t2)
                else:
                    r, cnt = t1.capitalize(), 1
                stash[r] = stash.get(r, 0) + cnt
                i += 2
            return stash

    for item in items:
        # Match '1x Ist' or '1 Ist'
        m1 = re.match(r"^(\d+)\s*[xX*]?\s*([A-Za-z]+)$", item)
        if m1:
            cnt = int(m1.group(1))
            r = m1.group(2).capitalize()
            stash[r] = stash.get(r, 0) + cnt
            continue

        # Match 'Ist: 1' or 'Ist = 1' or 'Ist 1'
        m2 = re.match(r"^([A-Za-z]+)\s*[:=\s]\s*(\d+)$", item)
        if m2:
            r = m2.group(1).capitalize()
            cnt = int(m2.group(2))
            stash[r] = stash.get(r, 0) + cnt
            continue

        # Single rune name without count -> default 1
        m3 = re.match(r"^([A-Za-z]+)$", item)
        if m3:
            r = m3.group(1).capitalize()
            stash[r] = stash.get(r, 0) + 1
            continue

    return stash


def prompt_choice(prompt_text: str, options: list, default_idx: int = 0) -> int:
    """Prompt user to choose from a list of options."""
    print(f"\n{prompt_text}")
    for i, opt in enumerate(options, 1):
        if isinstance(opt, tuple):
            print(f"  [{i}] {opt[0]:<18} - {opt[1]}")
        else:
            print(f"  [{i}] {opt}")
    default_str = f" [{default_idx + 1}]" if default_idx is not None else ""
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(options)}){default_str}: ").strip()
            if not choice and default_idx is not None:
                return default_idx
            val = int(choice) - 1
            if 0 <= val < len(options):
                return val
            print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input; please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)


def prompt_stash_guided() -> Dict[str, int]:
    """Guide the user rune-by-rune through entering their stash."""
    print("\nGuided Stash Entry (press Enter to skip / leave 0):")
    stash: Dict[str, int] = {}
    for r in lk_gen.RUNE_ORDER:
        val_str = input(f"  Number of {r:<4} runes [0]: ").strip()
        if val_str:
            try:
                cnt = int(val_str)
                if cnt > 0:
                    stash[r] = cnt
            except ValueError:
                pass
    return stash


def prompt_stash_input() -> Dict[str, int]:
    """Prompt the user for their starting stash."""
    print("\nStarting Stash Inventory:")
    print("  You can enter runes in quick format (e.g. '1 Ist, 1 Gul, 2 Pul' or 'Ist: 1, Gul: 1')")
    print("  Or type 'guided' for step-by-step entry, or press Enter for empty stash.")
    
    try:
        user_in = input("\nStash input [empty]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)

    if not user_in:
        return {}
    if user_in.lower() in ["guided", "g", "step"]:
        return prompt_stash_guided()

    stash = parse_stash_string(user_in)
    if not stash and user_in.lower() not in ["none", "empty", "0"]:
        print(f"  Could not parse '{user_in}'. Defaulting to empty stash.")
    return stash


def run_interactive():
    """Main interactive loop."""
    print("=" * 68)
    print("   LOWER KURAST (LK) RUN PLANNER & MARKOV PROBABILITY COMPANION")
    print("   Based on reverse-engineered D2R superchest patterns (Fruit/fearedbliss)")
    print("=" * 68)

    while True:
        # 1. Target Selection
        target_idx = prompt_choice("Select your farming target:", POPULAR_TARGETS, default_idx=1)
        selected_target, _ = POPULAR_TARGETS[target_idx]

        if selected_target == "Custom Target":
            try:
                target_str = input("\nEnter custom target rune or runeword (e.g. 'Ohm', '2x Ber', 'Death'): ").strip()
            except (KeyboardInterrupt, EOFError):
                break
        elif selected_target.endswith(" Rune"):
            target_str = selected_target.split()[0]
        else:
            target_str = selected_target

        # 2. Player count selection
        player_options = [
            ("/players 7-8", "Recommended: Best High Rune yield & smooth progression"),
            ("/players 5-6", "Suboptimal: More direct Lo/Ber, at steep cost to Gul/Ohm/Sur"),
            ("/players 3-4", "Lower density setting"),
            ("/players 1-2", "Default single player (rarely optimal for LK)"),
        ]
        p_idx = prompt_choice("Select player count:", player_options, default_idx=0)
        p_setting = ["p7", "p5", "p3", "p1"][p_idx]

        # 3. Stash Inventory
        stash = prompt_stash_input()

        # 4. Calculation and display
        print("\nComputing exact absorbing Markov chain back-substitution...")
        try:
            result = lk_gen.analyze_stash_for_target(
                target=target_str,
                current_stash=stash,
                player_setting=p_setting,
                min_cube_rune="Pul"
            )
            print()
            print(lk_gen.format_analysis_report(result))
        except Exception as e:
            print(f"\n[ERROR] Calculation failed: {e}")

        # 5. Continue / tweak
        print("\nOptions:")
        print("  [1] Plan another target or tweak stash")
        print("  [2] Exit")
        try:
            again = input("\nChoice [1]: ").strip()
            if again == "2" or again.lower() in ["exit", "q", "quit"]:
                print("Happy grinding! May the superchests roll high.")
                break
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Exact absorbing Markov chain run planner for Lower Kurast superchests."
    )
    parser.add_argument(
        "--target", "-t",
        type=str,
        help="Target rune or runeword (e.g. 'Call to Arms', 'Vex', 'Infinity', '2x Ber')"
    )
    parser.add_argument(
        "--stash", "-s",
        type=str,
        default="",
        help="Current stash (e.g. 'Ist:1,Gul:1' or '1 Ist, 1 Gul, 2 Pul')"
    )
    parser.add_argument(
        "--players", "-p",
        type=str,
        default="p7",
        choices=["p7", "p5", "p3", "p1"],
        help="Player count setting (default: p7)"
    )
    parser.add_argument(
        "--min-cube", "-m",
        type=str,
        default="Pul",
        help="Minimum rune tier to pick up and cube (default: Pul)"
    )

    args = parser.parse_args()

    if args.target:
        # Non-interactive CLI mode
        stash_dict = parse_stash_string(args.stash)
        res = lk_gen.analyze_stash_for_target(
            target=args.target,
            current_stash=stash_dict,
            player_setting=args.players,
            min_cube_rune=args.min_cube
        )
        print(lk_gen.format_analysis_report(res))
    else:
        # Interactive mode
        run_interactive()


if __name__ == "__main__":
    main()
