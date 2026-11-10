# Using GenAI for JavaScript Library Description Generation

This repository contains the replication package for our study on whether Large Language Models (LLMs) can infer the purpose of JavaScript libraries from their names alone.

The study evaluates **OpenAI GPT-5.4-mini** on generating concise descriptions for npm libraries without providing source code, README files, or usage examples. The generated descriptions are compared with the official GitHub repository descriptions using semantic similarity and readability metrics.

---

## Research Questions

### RQ1

**To what extent do AI-generated descriptions semantically align with human-written documentation across different library popularity tiers and temperature settings?**

### RQ2

**How readable and concise are AI-generated library descriptions compared to human-written ones?**

---

## Dataset

The experiments use the JavaScript library dataset introduced by Wattanakriengkrai et al., which originally contains **1,500 npm libraries** evenly divided into three popularity tiers:

* **Top tier:** 500 libraries
* **Middle tier:** 500 libraries
* **Bottom tier:** 500 libraries

Each library is associated with its GitHub repository and official repository description.

During data preparation, libraries with missing repository descriptions or inaccessible GitHub repositories (HTTP 404) were removed. In total, **50 libraries** were excluded:

* **14** from the Top tier
* **9** from the Middle tier
* **27** from the Bottom tier

The final dataset contains **1,450 JavaScript libraries**, consisting of:

* **486** Top-tier libraries
* **491** Middle-tier libraries
* **473** Bottom-tier libraries

The official GitHub repository descriptions serve as the ground-truth references for evaluating the semantic similarity and readability of AI-generated descriptions.

Each record in the dataset includes:

* Library name
* GitHub repository description (ground truth)
* Popularity tier

---

## Methodology

### Prompt

Each library is queried independently using the following prompt:

```text
You are a JavaScript backend developer.
Provide a concise description for the JavaScript library named "{library_name}".
```

The model is **not** given any additional context such as:

* README files
* Source code
* Usage examples

---

## Model Configuration

Model:

* GPT-5.4-mini

Temperature settings:

* 0.0
* 0.2
* 0.4

Each prompt is executed **5 times** for every library and temperature. Results are averaged to reduce output randomness.

---

## Evaluation

### RQ1 — Semantic Alignment

Generated descriptions are compared with the official GitHub descriptions using:

* Sentence embeddings from **all-MiniLM-L6-v2**
* Cosine Similarity
* Word Count Difference

Higher cosine similarity indicates stronger semantic alignment between the generated and human-written descriptions.

---

### RQ2 — Readability

Readability is measured using the:

* Gunning Fog Index (GFI)

Lower GFI values indicate simpler and easier-to-read descriptions.

Statistical significance across popularity tiers is evaluated using the **Kruskal–Wallis test**.

---

## Repository Structure

Files are grouped by research question. Run the notebooks and scripts from the repository root.

```
.
├── description_fetcher.ipynb        # Collect GitHub repository descriptions
├── RQ_code.ipynb                    # Generate descriptions and compute metrics for RQ1 and RQ2
├── data/                            # Shared inputs
│   ├── {top,middle,bottom}_lib.csv  # Repository URLs and number of dependents per tier
│   ├── Ori_lib_list.csv             # Original 1,500 libraries with descriptions
│   └── lib_list.csv                 # Final 1,450 libraries: name, tier, human description, human GFI
├── rq1/                             # RQ1: semantic similarity and length
│   ├── {0,0.2,0.4}_Similarity.csv   # Per-library cosine similarity (mean/std/median over 5 runs)
│   ├── Average_Word_Count_Difference.csv
│   ├── summary_Mean_Evaluate.csv
│   ├── RQ1_result_Sim.png           # Cosine similarity by tier and temperature
│   ├── word_count_difference.png    # Word-count difference by tier and temperature
│   └── manual_analysis/
│       └── sample30_labeled.csv     # 30-library manual analysis with labels
├── rq2/                             # RQ2: readability
│   ├── {0,0.2,0.4}_description_RQ2.csv  # All generated descriptions (5 runs x 1,450 libraries) with cosine and GFI
│   ├── plot_gfi_difference.py       # Draws RQ2_result_GF.png
│   └── RQ2_result_GF.png            # GFI difference (generated - human) by tier and temperature
└── analysis/                        # Statistical tests for both RQs
    ├── analysis.py
    └── results.json
```

The generated descriptions are stored once, in `rq2/`, and are also the input for the RQ1 similarity files.

---

## Installation

Install the required packages:

```bash
pip install openai pandas sentence-transformers scikit-learn python-dotenv textstat scipy scikit-posthocs matplotlib
```

Create a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

---

## Reproducing the Experiments

1. Fetch GitHub repository descriptions:

```text
description_fetcher.ipynb
```

2. Run the experiments:

```text
RQ_code.ipynb
```

The notebook:

* Generates library descriptions using GPT-5.4-mini
* Executes each prompt five times for every temperature
* Computes cosine similarity
* Computes word count differences
* Computes Gunning Fog Index
* Aggregates results by popularity tier

---

## Summary of Findings

### RQ1

* Temperature (0.0, 0.2, 0.4) has no measurable effect on semantic alignment (Friedman test, p >= 0.12 in every tier, Kendall's W < 0.005).
* Popularity has a significant but small effect (Kruskal-Wallis p < 0.001, epsilon squared = 0.019). Bottom-tier (rarely used) libraries receive the least aligned descriptions (mean cosine 0.56 vs. 0.62 Middle and 0.61 Top). The Middle vs. Top difference is negligible (Cliff's delta about 0.10).
* Generated descriptions are about 25 words longer than the human-written ones. The increase is largest for Top-tier libraries.

### RQ2

* Generated descriptions are harder to read than human-written ones: median Gunning Fog Index 16.6 vs. 10.0, a median per-library difference of about +6 points, higher for 83% of libraries.
* The gap is largest for Bottom-tier libraries. Temperature has no effect.
* The result holds when human descriptions with fewer than five words are excluded.

### Manual analysis

* In a stratified sample of 30 libraries, 24 generated descriptions were correct, 2 partially correct and 4 hallucinated (Bottom 3/10, Middle 1/10, Top 0/10).
* Cosine similarity is informative on average but unreliable for individual descriptions.

---

## Revision Analysis

Scripts and outputs added for the revised paper. Run them from the repository root.

```bash
python analysis/analysis.py . analysis > analysis/results.json
python rq2/plot_gfi_difference.py analysis/per_library.csv rq2/RQ2_result_GF.png
```

* `analysis/analysis.py`: dataset statistics, Kruskal-Wallis with Dunn post-hoc tests (Holm) and effect sizes (epsilon squared, Cliff's delta), Friedman tests for temperature, Wilcoxon signed-rank tests for generated vs. human descriptions, and the GFI sensitivity analysis. Writes `analysis/per_library.csv` (per-library scores averaged over the five runs, not tracked).
* `analysis/results.json`: all statistics reported in the paper.
* `rq2/plot_gfi_difference.py`: draws the GFI-difference figure.
* `rq1/manual_analysis/sample30_labeled.csv`: the manual-analysis sample (10 libraries per tier, random seed 42, T = 0.0, run 1) with labels C = correct, P = partially correct, W = hallucinated. The labels were assigned by one rater and confirmed by a second reviewer (no inter-rater agreement was computed).
