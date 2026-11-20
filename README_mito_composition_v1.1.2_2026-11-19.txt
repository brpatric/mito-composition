README_mito_composition_v1.1.2_2026-11-19.txt
=============================================
README for mito_composition_v1.1.2_2026-11-19.py


PROVENANCE
----------
  Program      mito_composition
  Version      1.1.2
  Date         2026-11-19
  Files        mito_composition_v1.1.2_2026-11-19.py   (program)
               README_mito_composition_v1.1.2_2026-11-19.txt   (this file)
               example/            worked example: 18 lycosid mitogenomes
                                   from GenBank (fasta/, names_example.csv,
                                   and the expected output/)
  Author       L. Brian Patrick, Department of Biological Sciences,
               Dakota Wesleyan University, Mitchell, SD, USA
               ORCID 0000-0003-1969-9600
  Development  Program and README drafted with the assistance of
               Claude Opus 5.5 (Anthropic) on 2026-11-19, from specifications
               by the author, and reviewed by the author.
  Derived from plot_composition_skew.py (author's plotting script,
               2026-11-01). Figure style is unchanged.
  Tested with  Python 3.13.18, matplotlib 3.11.2, numpy 2.5.3, on the 18
               lycosid mitogenomes from GenBank listed in example/names_example.csv;
               results matched an independent count of A, T, G and C.
  Output tags  The program prints its name, version and date in the IDLE shell
               at each run, and writes "mito_composition v1.1.2 (2026-11-19)"
               into the metadata of the PNG (Software) and PDF (Creator)
               figures.

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

When the program is changed, increase the version number, update the date,
rename both files to match, and add a line to the version history in both.


DESCRIPTION
-----------
Calculates nucleotide composition and strand skew for a folder of mitogenome
FASTA files, writes a CSV results table, and draws two figures (no titles):

  AT_GC_content  AT and GC content (%) as stacked bars, species ordered from
                 highest to lowest AT content.
  AT_GC_skew     AT skew (below zero) and GC skew (above zero), species ordered
                 from highest to lowest GC skew.


REQUIREMENTS
------------
Python 3.8 or later (written for IDLE 3.13; Python Software Foundation,
2024), matplotlib 3.8 or later (Hunter, 2007), and numpy (Harris et al.,
2020).
If needed, install them from a terminal for the same Python that IDLE (or the
command line) uses:
  Windows:  py -3.13 -m pip install matplotlib numpy
  macOS:    python3.13 -m pip install matplotlib numpy


RUNNING IN IDLE (main method)
-----------------------------
Option A: edit the settings and press F5

1. Open mito_composition_v1.1.2_2026-11-19.py in IDLE (File > Open...).
2. Edit the SETTINGS block at the top:

     FASTA_DIR  = r"C:\Users\me\mitogenomes"         folder of FASTA files
     NAMES_CSV  = r"C:\Users\me\mitogenomes\names.csv"
     OUTPUT_DIR = None        None = same folder as NAMES_CSV
     PREFIX     = "Mitogenomes"   start of every output file name

   Keep the r before the opening quote on Windows paths.
   On a Mac a path looks like r"/Users/me/mitogenomes".
3. File > Save, then Run > Run Module (F5).

The IDLE shell prints the program version, each file written, any warnings,
and the output folder.

Option B: run again from the IDLE shell prompt

After one F5 run (Option A), the function run() stays available at the >>>
prompt of the IDLE shell. Call it with different inputs without editing the
file:

  >>> run(r"C:\Users\me\mitogenomes", r"C:\Users\me\lycosa_names.csv")
  >>> run(r"C:\Users\me\mitogenomes", r"C:\Users\me\pardosa_names.csv",
  ...     output_dir=r"C:\Users\me\results", prefix="Pardosa")

  run(fasta_dir, names_csv, output_dir=None, prefix="Mitogenomes")
    fasta_dir   folder of FASTA files
    names_csv   names CSV (File, Name, Bold)
    output_dir  output folder; None = same folder as names_csv
    prefix      start of every output file name

Use a different prefix (or output_dir) for each comparison so earlier results
are not overwritten. If you edit and save the .py file, press F5 again before
calling run() so the shell uses the new version.


RUNNING FROM THE COMMAND LINE (optional: bash / Terminal / PowerShell)
----------------------------------------------------------------------
The same program can be run without IDLE. Open a terminal (bash on Linux or
the cluster, Terminal on macOS, PowerShell or Command Prompt on Windows), move
to the folder holding the program, and run:

  python3 mito_composition_v1.1.2_2026-11-19.py FASTA_DIR NAMES_CSV [--out-dir DIR] [--prefix NAME]

  (On Windows use  py -3.13  in place of  python3.)

  FASTA_DIR        folder of FASTA files                       (required)
  NAMES_CSV        names CSV with columns File, Name, Bold     (required)
  --out-dir DIR    output folder (default: same folder as NAMES_CSV)
  --prefix NAME    start of every output file name (default: Mitogenomes)
  --version        print the program version and stop
  -h, --help       print this usage summary and stop

Examples (bash / macOS):

  cd ~/mito_scripts
  python3 mito_composition_v1.1.2_2026-11-19.py ~/mitogenomes ~/mitogenomes/names.csv
  python3 mito_composition_v1.1.2_2026-11-19.py ~/mitogenomes lycosa_names.csv \
          --out-dir ~/results --prefix Lycosa

Example (Windows PowerShell):

  py -3.13 mito_composition_v1.1.2_2026-11-19.py C:\Users\me\mitogenomes C:\Users\me\names.csv --prefix Lycosa

Put quotes around any path that contains spaces, e.g. "~/My Data/names.csv".
If the program is run with no arguments it uses the SETTINGS block in the
file, exactly as in IDLE.

To run several comparisons in one go from bash:

  for set in lycosa pardosa piratula; do
      python3 mito_composition_v1.1.2_2026-11-19.py ~/mitogenomes ${set}_names.csv --prefix ${set}
  done


INPUT 1: FASTA FOLDER
---------------------
One mitogenome per FASTA file. Upper or lower case is fine. Files in the folder
that are not listed in the names CSV are ignored, so one folder can hold all
your mitogenomes.

Orient every sequence on the same strand and start them at the same gene
(e.g. cox1); otherwise the skews are not comparable.


INPUT 2: NAMES CSV
------------------
Three columns with these headers (capitalisation does not matter):

  File   FASTA file name in FASTA_DIR, exactly as it appears (with extension)
  Name   Label for the table and figures, written as
         Genus species (GenBank accession)
  Bold   yes to set that label in bold; leave blank for normal text
         (y, true, 1 and x also count as yes)

Example (a few lines of names_example.csv, which lists 18 lycosid
mitogenomes from GenBank; the Lycosa rows are set in bold):

  File,Name,Bold
  Evippa_sp_China_mitogenome_COX1first.fasta,Evippa sp. (PV694320),
  Halocosa_hatanensis_China_mitogenome_COX1first.fasta,Halocosa hatanensis (MT174468),
  Lycosa_grahami_China_mitogenome_COX1first.fasta,Lycosa grahami (ON951647),yes
  Lycosa_shansia_China_mitogenome_COX1first.fasta,Lycosa shansia (OK032619),yes
  Pardosa_chapini_China_mitogenome_COX1first.fasta,Pardosa chapini (PV694294),

  The two rows marked yes are labelled in bold in both figures, e.g.
  Lycosa grahami (ON951647); rows with an empty Bold field are in normal
  text. The trailing comma (an empty Bold field) is fine, and the Bold column
  can be left out entirely if nothing is to be bolded.

In the figures the genus and species are italic; "sp.", "cf." and the
parenthetical GenBank accession stay upright. To leave a mitogenome out of a run,
delete its row (or keep separate names CSVs for different comparisons).
The order of rows in the CSV is the order of rows in the results table; the
figures are always sorted as described above.


OUTPUTS (in OUTPUT_DIR)
-----------------------
  <PREFIX>_composition.csv
  <PREFIX>_AT_GC_content.png / .tif / .pdf     (PNG and TIFF at 600 dpi; PDF vector)
  <PREFIX>_AT_GC_skew.png / .tif / .pdf

Existing files with the same names are overwritten.

Columns of <PREFIX>_composition.csv:

  Name              label from the names CSV
  File              FASTA file name
  Length (bp)       full sequence length, including any ambiguous bases
  Ambiguous bases   number of characters other than A, T, G, C (e.g. N)
  A (%) T (%) G (%) C (%)   each base as a percentage of A+T+G+C
  AT content (%)    (A + T) / (A + T + G + C) x 100
  GC content (%)    (G + C) / (A + T + G + C) x 100
  AT skew           (A - T) / (A + T)
  GC skew           (G - C) / (G + C)

Percentages are given to 2 decimal places and skews to 4.
Ambiguous bases are excluded from every calculation; the shell prints a note
for any mitogenome that contains them.

The skew formulas follow Perna and Kocher (1995). Figures are drawn with
matplotlib (Hunter, 2007); numpy (Harris et al., 2020) is used for bar
positions.


CITING
------
If results from this program are published, cite the skew formulas (Perna and
Kocher, 1995) and the software used (Python, matplotlib, numpy), and give the
program name and version: mito_composition v1.1.2 (2026-11-19).


CHANGING THE APPEARANCE
-----------------------
Below the SETTINGS block:
  AT_COLOR / GC_COLOR   bar colours (blue #2C6FAC, orange #C8701A)
  FIGSIZE               figure size in inches (7.2 x 4.2)
  DPI                   PNG/TIFF resolution (600)
  plt.rcParams          font and font size (DejaVu Sans, 9 pt)


MESSAGES AND PROBLEMS
---------------------
  WARNING: <file> not found in FASTA folder - skipped
      The File entry does not match a file in FASTA_DIR. Check spelling and
      the extension (.fasta vs .fa vs .fas).

  WARNING: <file> has N FASTA records - sequences joined
      The file holds more than one sequence. They are joined end to end, which
      is only correct if they are pieces of the same mitogenome.

  note: <name> has N ambiguous bases (excluded)
      Information only; the values use A, T, G and C.

  FileNotFoundError: FASTA folder / Names CSV not found
      Fix the path in SETTINGS (use the full path; keep the r on Windows).

  ValueError: ... needs a 'File' (or 'Name') column
      The names CSV headers are missing or misspelled.

  ModuleNotFoundError: No module named 'matplotlib' (or numpy)
      Install the packages for IDLE's Python (see REQUIREMENTS).

  Labels use a different font
      DejaVu Sans is not installed; change "font.family" in plt.rcParams,
      e.g. to "Arial".


REFERENCES
----------
DOIs were checked against the publisher, PubMed or the software's own citation
file on 2026-11-19.

Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P.,
  Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R.,
  Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A.,
  del Rio, J. F., Wiebe, M., Peterson, P., Gerard-Marchant, P., Sheppard, K.,
  Reddy, T., Weckesser, W., Abbasi, H., Gohlke, C., & Oliphant, T. E. (2020).
  Array programming with NumPy. Nature, 585(7825), 357-362.
  https://doi.org/10.1038/s41586-020-2649-2

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in
  Science & Engineering, 9(3), 90-95. https://doi.org/10.1109/MCSE.2007.55

Perna, N. T., & Kocher, T. D. (1995). Patterns of nucleotide composition at
  fourfold degenerate sites of animal mitochondrial genomes. Journal of
  Molecular Evolution, 41(3), 353-358. https://doi.org/10.1007/BF00186547

Python Software Foundation. (2024). Python (Version 3.13) [Computer software].
  https://www.python.org/  (no DOI)
