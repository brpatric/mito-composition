#!/usr/bin/env python3
r"""
mito_composition_v1.1.2_2026-11-19.py

Nucleotide composition and strand skew for a folder of mitogenome FASTA files.

PROVENANCE
  Program   : mito_composition
  Version   : 1.1.2
  Date      : 2026-11-19
  Author    : L. Brian Patrick, Department of Biological Sciences,
              Dakota Wesleyan University, Mitchell, SD, USA
              ORCID 0000-0003-1969-9600
  Development: Code drafted with the assistance of Claude Opus 5.5 (Anthropic),
              2026-11-19, from specifications by the author, and reviewed by
              the author.
  Derived from: plot_composition_skew.py (author's plotting script,
              2026-11-01). Figure style is unchanged.
  Tested with: Python 3.13.18, matplotlib 3.11.2, numpy 2.5.3, on the 18
              lycosid mitogenomes from GenBank listed in example/names_example.csv;
              values matched an independent count of A, T, G and C.
  Companion  : README_mito_composition_v1.1.2_2026-11-19.txt
  Version history
    1.0.0  2026-11-19  First release.
    1.1.0  2026-11-19  Added optional command-line (bash) arguments;
                       running from IDLE is unchanged.
    1.1.1  2026-11-19  Documentation only: examples now use only published
                       GenBank mitogenomes; calculations and figures unchanged.
    1.1.2  2026-11-19  Figures only: no extra space between "sp." and the
                       accession in labels; skew axis now extends to the next
                       tick mark so the lowest and highest ticks are labelled.
                       Calculations unchanged.

HOW TO USE (IDLE 3.13)
  1. Open this file in IDLE.
  2. Edit the four SETTINGS below.
  3. Save, then press F5 (Run > Run Module).
  After one F5 run, run() can be called again from the IDLE shell prompt:
    >>> run(r"C:\path\fasta_folder", r"C:\path\names.csv", prefix="Lycosa")

OPTIONAL: COMMAND LINE (bash, macOS Terminal, Windows PowerShell)
  python3 mito_composition_v1.1.2_2026-11-19.py FASTA_DIR NAMES_CSV [--out-dir DIR] [--prefix NAME]
  With no arguments, the SETTINGS below are used.

INPUTS
  FASTA_DIR  : folder containing the mitogenome FASTA files (one mitogenome per file)
  NAMES_CSV  : CSV file with three columns:
                   File  - FASTA file name in FASTA_DIR
                   Name  - label used in the table and figures, written as
                           Genus species (GenBank accession),
                           e.g. "Lycosa grahami (ON951647)"
                   Bold  - yes to set that label in bold; leave blank otherwise
               Only the files listed in NAMES_CSV are analysed.

OUTPUTS (written to OUTPUT_DIR)
  <PREFIX>_composition.csv        table of composition and skew values
  <PREFIX>_AT_GC_content.png/.tif/.pdf   stacked AT/GC content, highest -> lowest AT
  <PREFIX>_AT_GC_skew.png/.tif/.pdf      AT and GC skew, highest -> lowest GC skew

CALCULATIONS (ambiguous bases such as N are excluded)
  A, T, G, C (%)   = base / (A + T + G + C) x 100
  AT content (%)   = (A + T) / (A + T + G + C) x 100
  GC content (%)   = (G + C) / (A + T + G + C) x 100
  AT skew          = (A - T) / (A + T)
  GC skew          = (G - C) / (G + C)        (Perna & Kocher 1995)

Requires: matplotlib, numpy  (pip install matplotlib numpy)

REFERENCES (DOIs verified 2026-11-19)
  Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array
    programming with NumPy. Nature, 585(7825), 357-362.
    https://doi.org/10.1038/s41586-020-2649-2
  Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in
    Science & Engineering, 9(3), 90-95. https://doi.org/10.1109/MCSE.2007.55
  Perna, N. T., & Kocher, T. D. (1995). Patterns of nucleotide composition at
    fourfold degenerate sites of animal mitochondrial genomes. Journal of
    Molecular Evolution, 41(3), 353-358. https://doi.org/10.1007/BF00186547
"""

# =========================================================================
# SETTINGS - edit these, save, and press F5
# On Windows keep the r in front of the quotes:  r"C:\Users\me\mitogenomes"
# =========================================================================
FASTA_DIR = r"C:\path\to\fasta_folder"
NAMES_CSV = r"C:\path\to\names.csv"
OUTPUT_DIR = None          # None = save results in the same folder as NAMES_CSV
PREFIX = "Mitogenomes"     # start of every output file name
# =========================================================================

import argparse
import csv
import os
import re
import sys

__program__ = "mito_composition"
__version__ = "1.1.2"
__date__ = "2026-11-19"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---- figure appearance ----
AT_COLOR = "#2C6FAC"    # blue
GC_COLOR = "#C8701A"    # orange
FIGSIZE = (7.2, 4.2)    # inches
DPI = 600
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

YES = {"yes", "y", "true", "t", "1", "x", "bold"}


# -------------------------------------------------------------------------
# Reading inputs
# -------------------------------------------------------------------------
def read_names(names_csv):
    """Return a list of dicts with keys file, name, bold (in CSV order)."""
    with open(names_csv, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        cols = {c.strip().lower(): c for c in (reader.fieldnames or [])}
        for need in ("file", "name"):
            if need not in cols:
                raise ValueError(f"{names_csv} needs a '{need.title()}' column. "
                                 f"Found: {reader.fieldnames}")
        rows = []
        for r in reader:
            f = (r.get(cols["file"]) or "").strip()
            if not f:
                continue
            name = (r.get(cols["name"]) or "").strip() or f
            bold = (r.get(cols["bold"]) or "").strip().lower() in YES if "bold" in cols else False
            rows.append({"file": f, "name": name, "bold": bold})
    if not rows:
        raise ValueError(f"No rows found in {names_csv}")
    return rows


def read_fasta(path):
    """Return the sequence (upper case, no whitespace) and number of records."""
    seq, records = [], 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(">"):
                records += 1
            else:
                seq.append(line.strip())
    return "".join(seq).upper().replace(" ", ""), records


# -------------------------------------------------------------------------
# Calculations
# -------------------------------------------------------------------------
def composition(seq):
    a, t, g, c = (seq.count(b) for b in "ATGC")
    n = a + t + g + c
    if n == 0:
        raise ValueError("no A, T, G or C found")
    return {
        "Length (bp)": len(seq),
        "Ambiguous bases": len(seq) - n,
        "A (%)": 100 * a / n,
        "T (%)": 100 * t / n,
        "G (%)": 100 * g / n,
        "C (%)": 100 * c / n,
        "AT content (%)": 100 * (a + t) / n,
        "GC content (%)": 100 * (g + c) / n,
        "AT skew": (a - t) / (a + t),
        "GC skew": (g - c) / (g + c),
    }


# -------------------------------------------------------------------------
# Figures
# -------------------------------------------------------------------------
def label(name, bold):
    """Italic genus/species, roman parenthetical and 'sp.'; optional bold."""
    m = re.match(r"^\s*(.+?)\s*(\(.*\))?\s*$", name)
    taxon, paren = m.group(1), (m.group(2) or "")
    it, rm = (r"\mathbfit", r"\mathbf") if bold else (r"\mathit", r"\mathrm")
    esc = lambda s: s.replace("\\", "").replace(" ", r"\ ").replace("_", r"\_") \
                     .replace("%", r"\%").replace("$", r"\$").replace("&", r"\&")
    words = taxon.split() + ([paren] if paren else [])
    text = ""
    for i, w in enumerate(words):
        roman = (i == len(words) - 1 and bool(paren)) or \
            w in ("sp.", "spp.", "cf.", "aff.") or not w[:1].isalpha()
        if i:
            # mathtext already adds space after a full stop, so use a thin space
            text += r"\," if words[i - 1].endswith(".") else r"\ "
        text += f"{rm if roman else it}{{{esc(w)}}}"
    return f"${text}$"


def save(fig, base):
    made_by = f"{__program__} v{__version__} ({__date__})"
    fig.savefig(base + ".png", dpi=DPI, metadata={"Software": made_by})
    fig.savefig(base + ".tif", dpi=DPI, pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(base + ".pdf", metadata={"Creator": made_by})
    plt.close(fig)
    print("  wrote", os.path.basename(base) + ".png / .tif / .pdf")


def axes_common(ax, rows, ylabel):
    x = np.arange(len(rows))
    ax.set_xticks(x)
    ax.set_xticklabels([label(r["name"], r["bold"]) for r in rows],
                       rotation=55, ha="right", rotation_mode="anchor", fontsize=8)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(True, color="#e3e3e3", lw=0.6)
    ax.set_axisbelow(True)


def plot_content(rows, base):
    rows = sorted(rows, key=lambda r: -r["AT content (%)"])
    x = np.arange(len(rows))
    at = [r["AT content (%)"] for r in rows]
    gc = [r["GC content (%)"] for r in rows]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(x, at, 0.7, color=AT_COLOR, label="AT content", edgecolor="white", linewidth=0.8)
    ax.bar(x, gc, 0.7, bottom=at, color=GC_COLOR, label="GC content", edgecolor="white", linewidth=0.8)
    axes_common(ax, rows, "Nucleotide content (%)")
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout()
    save(fig, base)


def plot_skew(rows, base):
    rows = sorted(rows, key=lambda r: -r["GC skew"])
    x = np.arange(len(rows))
    ats = [r["AT skew"] for r in rows]
    gcs = [r["GC skew"] for r in rows]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(x, ats, 0.7, color=AT_COLOR, label="AT skew", edgecolor="white", linewidth=0.8)
    ax.bar(x, gcs, 0.7, color=GC_COLOR, label="GC skew", edgecolor="white", linewidth=0.8)
    ax.axhline(0, color="#333333", lw=0.8)
    axes_common(ax, rows, "Skew")
    lo = min(-0.05, min(ats + gcs) * 1.15)
    hi = max(0.05, max(ats + gcs) * 1.15)
    # extend the axis to the tick marks just beyond the data, so the lowest
    # and highest ticks are labelled
    dlo, dhi = min(ats + gcs), max(ats + gcs)
    ax.set_ylim(lo, hi)
    for _ in range(3):
        t = ax.get_yticks()
        new = (t[t <= min(dlo, -0.05) + 1e-9].max(), t[t >= max(dhi, 0.05) - 1e-9].min())
        if np.allclose(new, ax.get_ylim()):
            break
        ax.set_ylim(*new)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout()
    save(fig, base)


# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------
COLUMNS = ["Name", "File", "Length (bp)", "Ambiguous bases",
           "A (%)", "T (%)", "G (%)", "C (%)",
           "AT content (%)", "GC content (%)", "AT skew", "GC skew"]


def run(fasta_dir=FASTA_DIR, names_csv=NAMES_CSV, output_dir=OUTPUT_DIR, prefix=PREFIX):
    print(f"{__program__} v{__version__} ({__date__})")
    fasta_dir = os.path.abspath(os.path.expanduser(fasta_dir))
    names_csv = os.path.abspath(os.path.expanduser(names_csv))
    if not os.path.isdir(fasta_dir):
        raise FileNotFoundError(f"FASTA folder not found: {fasta_dir}")
    if not os.path.isfile(names_csv):
        raise FileNotFoundError(f"Names CSV not found: {names_csv}")
    output_dir = os.path.abspath(output_dir or os.path.dirname(names_csv))
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.join(output_dir, prefix)

    rows = []
    for entry in read_names(names_csv):
        path = os.path.join(fasta_dir, entry["file"])
        if not os.path.isfile(path):
            print(f"  WARNING: {entry['file']} not found in FASTA folder - skipped")
            continue
        seq, nrec = read_fasta(path)
        if nrec != 1:
            print(f"  WARNING: {entry['file']} has {nrec} FASTA records - sequences joined")
        comp = composition(seq)
        if comp["Ambiguous bases"]:
            print(f"  note: {entry['name']} has {comp['Ambiguous bases']} ambiguous bases (excluded)")
        rows.append({"Name": entry["name"], "File": entry["file"],
                     "name": entry["name"], "bold": entry["bold"], **comp})

    if not rows:
        raise SystemExit("No mitogenomes were analysed - check FASTA_DIR and the File column.")

    # results table
    out_csv = base + "_composition.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for r in rows:
            vals = []
            for col in COLUMNS:
                v = r[col]
                if isinstance(v, float):
                    v = f"{v:.4f}" if "skew" in col else f"{v:.2f}"
                vals.append(v)
            w.writerow(vals)
    print("  wrote", os.path.basename(out_csv))

    plot_content(rows, base + "_AT_GC_content")
    plot_skew(rows, base + "_AT_GC_skew")
    print(f"Done: {len(rows)} mitogenomes. Results saved in: {output_dir}")
    return rows


def main():
    """IDLE / no arguments: use SETTINGS. Command line: use the arguments."""
    if len(sys.argv) == 1:
        run()
        return
    ap = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description="Nucleotide composition and strand skew for mitogenome FASTA files.")
    ap.add_argument("fasta_dir", help="folder containing the mitogenome FASTA files")
    ap.add_argument("names_csv", help="CSV with columns File, Name, Bold")
    ap.add_argument("--out-dir", default=None,
                    help="output folder (default: same folder as NAMES_CSV)")
    ap.add_argument("--prefix", default="Mitogenomes",
                    help="start of every output file name (default: Mitogenomes)")
    ap.add_argument("--version", action="version",
                    version=f"{__program__} {__version__} ({__date__})")
    a = ap.parse_args()
    run(a.fasta_dir, a.names_csv, a.out_dir, a.prefix)


if __name__ == "__main__":
    main()
