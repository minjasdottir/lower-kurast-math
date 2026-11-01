#!/usr/bin/env bash
# Regenerate all figures and compile the Lower Kurast paper (Stop Doing Random Shit in Lower Kurast.pdf).
# Usage:
#   ./build.sh           # Regenerate figures + compile paper
#   ./build.sh --tex     # Compile paper only (skip figure generation)
#   ./build.sh --verify  # Also run the mathematical verification scripts

set -euo pipefail

cd "$(dirname "$0")"

if [[ "${1:-}" == "--verify" ]]; then
    echo "==> Running mathematical verification scripts..."
    python3 lk_math.py
    python3 lk_cubing.py
fi

if [[ "${1:-}" != "--tex" ]]; then
    echo "==> Generating vector PDF figures (lk_figures.pdf, lk_cubing_figures.pdf, lk_markov_board.pdf)..."
    python3 generate_plots.py
fi

echo "==> Compiling main.tex -> Stop Doing Random Shit in Lower Kurast.pdf via Tectonic..."
tectonic main.tex
mv -f main.pdf "Stop Doing Random Shit in Lower Kurast.pdf"

echo "==> Done! Output written to $(pwd)/Stop Doing Random Shit in Lower Kurast.pdf"
