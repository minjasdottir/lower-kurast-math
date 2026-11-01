#!/usr/bin/env python3
"""
Generate publication-quality figures for the Lower Kurast paper:
1. lk_figures.pdf: Dry spell survival curves & efficiency penalty under Fruit's d2pg model
2. lk_cubing_figures.pdf: Absorbing Markov chain CDFs for Lo (and Ber) on /players 7 vs /players 5
"""

import numpy as np
import matplotlib.pyplot as plt
from lk_cubing import (
    PATTERNS_P7,
    PATTERNS_P5,
    TOTAL_PATTERNS,
    weighted_patterns,
    compute_cdf_curves,
    absorbing_markov_expected_runs,
)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "legend.fontsize": 8.8,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 300,
})

# Exact pattern count from Fruit's d2pg (verified by fearedbliss, and documented by TheHappyDev at https://d2runes.io/rune-farming/lk-farming)
VEX_BER_PATTERNS_P7 = 24.0  # Fruit's d2pg exact count (6 Vex + 5 Ohm + 2 Lo + 9 Sur + 2 Ber)
p_chest = VEX_BER_PATTERNS_P7 / TOTAL_PATTERNS
p_run = 1.0 - (1.0 - p_chest) ** 6
mu_T = 1.0 / p_run


def make_figure_1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))

    # Panel A: Survival probabilities S(n) and career dry spell probabilities
    n = np.arange(0, 2701)
    S_n = (1.0 - p_run) ** n
    career_10 = 1.0 - (1.0 - S_n) ** 10
    career_15 = 1.0 - (1.0 - S_n) ** 15

    ax1.plot(n, S_n * 100, color="#1f4e78", lw=2.2, label=r"Single wait $S(n) = \mathbb{P}(T > n)$")
    ax1.plot(n, career_10 * 100, color="#2e8b57", lw=1.8, ls="--", label=r"At least once in $M = 10$ HRs")
    ax1.plot(n, career_15 * 100, color="#b22222", lw=1.8, ls="-.", label=r"At least once in $M = 15$ HRs")

    ax1.axvspan(2000, 2460, color="#f4a582", alpha=0.30, label="Dead_Sett drought ($2{,}000$–$2{,}460$ runs)")
    ax1.axvline(mu_T, color="gray", lw=1.0, ls=":")
    ax1.text(
        mu_T + 35, 56, f"Mean\n{mu_T:.0f} runs",
        fontsize=8.5, color="#333333",
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.85),
    )

    s2000 = ((1.0 - p_run) ** 2000) * 100
    s2460 = ((1.0 - p_run) ** 2460) * 100
    c15_2000 = (1.0 - (1.0 - (1.0 - p_run) ** 2000) ** 15) * 100
    c15_2460 = (1.0 - (1.0 - (1.0 - p_run) ** 2460) ** 15) * 100

    ax1.scatter([2000, 2460], [s2000, s2460], color="#1f4e78", zorder=5, s=28)
    ax1.scatter([2000, 2460], [c15_2000, c15_2460], color="#b22222", zorder=5, s=28)

    label_bbox = dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.85)
    ax1.annotate(f"{s2000:.2f}%", (2000, s2000), xytext=(1640, s2000 + 2.5), fontsize=8.0, color="#1f4e78", fontweight="bold", bbox=label_bbox, zorder=6)
    ax1.annotate(f"{s2460:.2f}%", (2460, s2460), xytext=(2170, s2460 + 0.8), fontsize=8.0, color="#1f4e78", fontweight="bold", bbox=label_bbox, zorder=6)
    ax1.annotate(f"{c15_2000:.1f}%", (2000, c15_2000), xytext=(2035, c15_2000 + 3.5), fontsize=8.0, color="#b22222", fontweight="bold", bbox=label_bbox, zorder=6)
    ax1.annotate(f"{c15_2460:.1f}%", (2460, c15_2460), xytext=(2280, c15_2460 + 5.5), fontsize=8.0, color="#b22222", fontweight="bold", bbox=label_bbox, zorder=6)

    ax1.set_title("(a) Dry Spell Survival & Career Drought Probability")
    ax1.set_xlabel("Consecutive Barren Runs ($n$)")
    ax1.set_ylabel("Probability (%)")
    ax1.set_xlim(0, 2700)
    ax1.set_ylim(0, 102)
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper right", frameon=True)

    # Panel B: Efficiency penalty
    delta_t = np.linspace(0, 25, 200)
    for t0, color, label in [
        (20.0, "#1f4e78", r"Fast base run ($\tau_0 = 20$ s)"),
        (25.0, "#2e8b57", r"Standard base run ($\tau_0 = 25$ s)"),
        (30.0, "#b22222", r"Relaxed base run ($\tau_0 = 30$ s)"),
    ]:
        hrs_per_100h = (100.0 * 3600.0 / (t0 + delta_t)) * p_run
        ax2.plot(delta_t, hrs_per_100h, lw=2.0, color=color, label=label)

    ax2.axvline(10.0, color="#555555", ls="--", lw=1.1)
    y_25_0 = (100.0 * 3600.0 / 25.0) * p_run
    y_25_10 = (100.0 * 3600.0 / 35.0) * p_run
    ax2.scatter([0, 10], [y_25_0, y_25_10], color="#2e8b57", zorder=5, s=30)
    ax2.annotate(
        f"$\\Delta\\tau = +10$ s:\n$-28.6\\%$ yield\n({y_25_0:.1f} $\\to$ {y_25_10:.1f} HRs)",
        xy=(10, y_25_10),
        xytext=(12.0, y_25_10 + 4.0),
        arrowprops=dict(arrowstyle="->", color="#333333", lw=0.9),
        fontsize=8.5,
    )

    ax2.set_title(r"(b) Cost of Superstition: Yield vs. Extra Time $\Delta\tau$")
    ax2.set_xlabel(r'Extra Time Spent on "Random Actions" per Run $\Delta\tau$ (seconds)')
    ax2.set_ylabel("Expected High Runes (Vex–Ber) per 100 Hours")
    ax2.set_xlim(0, 25)
    ax2.set_ylim(12, 43)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    plt.savefig("lk_figures.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Saved lk_figures.pdf")


def make_figure_2():
    """
    Figure 2:
    Left panel: Cumulative probability F(n) of acquiring a Lo rune on /players 7 vs /players 5
      comparing direct drops vs cubing Pul+ (showing the /p5 -> /p7 crossover at n = 1,353 runs!).
    Right panel: Expected runs E[R] to acquire each target rune (Vex, Ohm, Lo, Sur, Ber)
      comparing Direct Drops vs Cubing (Gul+) vs Cubing (Pul+) on /players 7 and /players 5.
    """
    w7 = weighted_patterns(PATTERNS_P7, 0.20)
    w5 = weighted_patterns(PATTERNS_P5, 0.20)

    max_runs = 3600
    n = np.arange(0, max_runs + 1)

    cdf_lo_p7_pul = compute_cdf_curves(w7, "Lo", "Pul", max_runs)
    cdf_lo_p5_pul = compute_cdf_curves(w5, "Lo", "Pul", max_runs)
    cdf_lo_p7_dir = compute_cdf_curves(w7, "Lo", "Lo", max_runs)
    cdf_lo_p5_dir = compute_cdf_curves(w5, "Lo", "Lo", max_runs)

    # Find exact crossover run where cdf_lo_p7_pul >= cdf_lo_p5_pul
    crossover_idx = int(np.where(cdf_lo_p7_pul[1:] >= cdf_lo_p5_pul[1:])[0][0] + 1)
    crossover_prob = cdf_lo_p7_pul[crossover_idx] * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))

    ax1.plot(n, cdf_lo_p7_pul * 100, color="#1f4e78", lw=2.3, label=r"$\mathtt{/players\ 7}$ (Cubing Pul$\to$Lo, $\mathbb{E}[R]=1{,}570$)")
    ax1.plot(n, cdf_lo_p5_pul * 100, color="#b22222", lw=2.1, ls="--", label=r"$\mathtt{/players\ 5}$ (Cubing Pul$\to$Lo, $\mathbb{E}[R]=1{,}714$)")
    ax1.plot(n, cdf_lo_p5_dir * 100, color="#d95f02", lw=1.6, ls="-.", label=r"$\mathtt{/players\ 5}$ (Direct Lo only, $\mathbb{E}[R]=2{,}731$)")
    ax1.plot(n, cdf_lo_p7_dir * 100, color="#7570b3", lw=1.6, ls=":", label=r"$\mathtt{/players\ 7}$ (Direct Lo only, $\mathbb{E}[R]=5{,}462$)")

    ax1.scatter([crossover_idx], [crossover_prob], color="#111111", zorder=6, s=32)
    ax1.annotate(
        f"Crossover: $n = {crossover_idx}$ runs\n($F(n) = {crossover_prob:.1f}\\%$)",
        xy=(crossover_idx, crossover_prob),
        xytext=(320, 66),
        arrowprops=dict(arrowstyle="->", color="#222222", lw=0.9),
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#cccccc", alpha=0.92),
        fontsize=8.3,
        fontweight="bold",
    )

    ax1.axhline(50.0, color="gray", lw=0.8, ls=":")
    ax1.set_title("(a) Cumulative Probability of Acquiring a Lo Rune")
    ax1.set_xlabel("Number of 6-Chest Lower Kurast Runs ($n$)")
    ax1.set_ylabel("Probability of At Least One Lo Rune (%)")
    ax1.set_xlim(0, max_runs)
    ax1.set_ylim(0, 100)
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="lower right", frameon=True)

    # Panel B: Bar chart comparing Expected Runs E[R] for Vex, Ohm, Lo, Sur, Ber (Cubing Pul+) on /p7 vs /p5
    targets = ["Vex", "Ohm", "Lo", "Sur", "Ber"]
    e7_pul = [absorbing_markov_expected_runs(w7, r, "Pul")[0] for r in targets]
    e5_pul = [absorbing_markov_expected_runs(w5, r, "Pul")[0] for r in targets]
    e7_gul = [absorbing_markov_expected_runs(w7, r, "Gul")[0] for r in targets]
    e5_gul = [absorbing_markov_expected_runs(w5, r, "Gul")[0] for r in targets]

    x = np.arange(len(targets))
    width = 0.20

    rects1 = ax2.bar(x - 1.5 * width, e7_pul, width, label=r"$\mathtt{/p7}$ (Cube Pul+)", color="#1f4e78")
    rects2 = ax2.bar(x - 0.5 * width, e5_pul, width, label=r"$\mathtt{/p5}$ (Cube Pul+)", color="#b22222")
    rects3 = ax2.bar(x + 0.5 * width, e7_gul, width, label=r"$\mathtt{/p7}$ (Cube Gul+)", color="#6baed6")
    rects4 = ax2.bar(x + 1.5 * width, e5_gul, width, label=r"$\mathtt{/p5}$ (Cube Gul+)", color="#fc9272")

    ax2.set_title("(b) Expected Runs to Target Rune (With Cubing)")
    ax2.set_xlabel("Target Rune")
    ax2.set_ylabel(r"Expected 6-Chest Runs $\mathbb{E}[R]$")
    ax2.set_xticks(x)
    ax2.set_xticklabels(targets)
    ax2.set_ylim(0, 2350)
    ax2.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", ncol=2, frameon=True)

    for rect_idx, rect in enumerate([rects1, rects2]):
        for bar_i, bar in enumerate(rect):
            h = bar.get_height()
            if rect_idx == 0:
                dx, dy = -4.5, 2
            elif bar_i == 4:
                dx, dy = 2.5, 7
            elif bar_i == 2:
                dx, dy = -1.5, 3
            else:
                dx, dy = 0.0, 2
            ax2.annotate(
                f"{h:.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(dx, dy),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=6.6,
            )

    plt.tight_layout()
    plt.savefig("lk_cubing_figures.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved lk_cubing_figures.pdf (Lo crossover at n = {crossover_idx} runs)")


def make_markov_board_figure():
    """
    Create a visual, geometric diagram of the 9-state Gul -> Lo absorbing Markov chain
    board game (states 0 through 8, where 1 Gul = 1, 1 Vex = 2, 1 Ohm = 4, 1 Lo = 8),
    alongside a visual depiction of the 9x9 upper-triangular transition matrix.
    """
    import matplotlib.patches as patches

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.45, 1.0]})

    # Left Panel: The 9-square board game from 0 to 8
    ax1.set_xlim(-0.6, 8.95)
    ax1.set_ylim(-1.55, 2.50)
    ax1.axis("off")
    ax1.set_title(r"(a) Geometric View: The $\text{Gul}\to\text{Lo}$ Cubing Board ($W = 8$ Gul Units)", pad=12)

    for s in range(9):
        is_goal = (s == 8)
        face = "#d95f02" if is_goal else ("#e8f1f5" if s > 0 else "#ffffff")
        edge = "#8c2d04" if is_goal else "#1f4e78"
        lw = 2.2 if is_goal else 1.5
        box = patches.FancyBboxPatch(
            (s - 0.36, -0.35), 0.72, 0.70,
            boxstyle="round,pad=0.04",
            facecolor=face, edgecolor=edge, linewidth=lw, zorder=3
        )
        ax1.add_patch(box)
        txt_color = "white" if is_goal else "#111111"
        ax1.text(s, 0.0, f"{s}", ha="center", va="center", fontsize=11, fontweight="bold", color=txt_color, zorder=4)

    ax1.text(0, -0.68, "Start\n(Empty)", ha="center", va="top", fontsize=8.5, color="#333333")
    ax1.text(4, -0.68, "Halfway\n(e.g. 1 Ohm\nor 2 Vex)", ha="center", va="top", fontsize=8.0, color="#333333")
    ax1.text(8, -0.68, "Absorbing Goal\n(1 Lo crafted!)", ha="center", va="top", fontsize=8.5, fontweight="bold", color="#8c2d04")

    # Draw jump arcs from State 0
    jumps = [
        (1, 0.48, "#2e8b57", "+1 (Gul)", 0.65, 0.85),
        (2, 0.88, "#1f4e78", "+2 (Vex)", 1.38, 1.26),
        (4, 1.30, "#7570b3", "+4 (Ohm)", 2.65, 1.68),
        (8, 1.74, "#b22222", "+8 (Direct Lo)", 4.00, 2.13),
    ]
    arc_bbox = dict(boxstyle="round,pad=0.08", facecolor="white", edgecolor="none", alpha=0.88)
    for target, rad_h, col, label, lx, ly in jumps:
        x_mid = target / 2.0
        t = np.linspace(0, np.pi, 60)
        xs = x_mid - x_mid * np.cos(t)
        ys = 0.35 + rad_h * np.sin(t)
        ax1.plot(xs, ys, color=col, lw=1.6, zorder=2)
        # Arrowhead at end
        ax1.annotate(
            "", xy=(target, 0.36), xytext=(xs[-3], ys[-3]),
            arrowprops=dict(arrowstyle="->", color=col, lw=1.6), zorder=5
        )
        ax1.text(
            lx, ly, label,
            ha="center", va="bottom", fontsize=8.0, color=col, fontweight="bold",
            bbox=arc_bbox, zorder=6,
        )

    # Self-loop at state 8 (absorbing)
    theta = np.linspace(-0.3 * np.pi, 1.3 * np.pi, 50)
    ax1.plot(8 + 0.28 * np.cos(theta), 0.55 + 0.22 * np.sin(theta), color="#8c2d04", lw=1.5)
    ax1.text(
        8.42, 0.82, "Stays at 8\n($P_{8,8}=1$)",
        ha="center", va="bottom", fontsize=7.5, color="#8c2d04",
        bbox=arc_bbox, zorder=6,
    )

    # Right Panel: Structure of the 9x9 Upper-Triangular Transition Matrix P
    mat = np.zeros((9, 9))
    for i in range(8):
        mat[i, i] = 0.35  # self loop (no drop)
        if i + 1 <= 8:
            mat[i, min(8, i + 1)] += 0.25  # +1 Gul
        if i + 2 <= 8:
            mat[i, min(8, i + 2)] += 0.20  # +2 Vex
        if i + 4 <= 8:
            mat[i, min(8, i + 4)] += 0.15  # +4 Ohm
        mat[i, 8] += 0.05  # clamped jumps to 8
    mat[8, 8] = 1.0  # absorbing

    im = ax2.imshow(mat, cmap="Blues", vmin=0, vmax=1.0)
    ax2.set_title("(b) Linear Algebra View: Upper-Triangular Matrix $P$", pad=8)
    ax2.set_xlabel("Next State $j$ (After Chest/Run)")
    ax2.set_ylabel("Current State $i$ (Before Chest/Run)")
    ax2.set_xticks(range(9))
    ax2.set_yticks(range(9))

    for i in range(9):
        for j in range(9):
            if i > j:
                ax2.text(j, i, "0", ha="center", va="center", fontsize=7.5, color="#aaaaaa")
            elif i == 8 and j == 8:
                ax2.text(j, i, "1", ha="center", va="center", fontsize=8.5, fontweight="bold", color="white")
            elif mat[i, j] > 0:
                symbol = r"$p_0$" if i == j else (r"$*$" if j == 8 else f"+{j-i}")
                ax2.text(j, i, symbol, ha="center", va="center", fontsize=7.2, color="#08306b", fontweight="bold")

    ax2.text(2.2, 6.3, "Strictly Zero\nBelow Diagonal\n(Never Lose Runes!)", ha="center", va="center",
             fontsize=8.2, color="#555555", bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9))

    plt.tight_layout()
    plt.savefig("lk_markov_board.pdf", bbox_inches="tight")
    plt.close(fig)
    print("Saved lk_markov_board.pdf")


if __name__ == "__main__":
    make_figure_1()
    make_figure_2()
    make_markov_board_figure()
