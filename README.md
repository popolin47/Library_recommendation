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

```
.
├── github_description_fetcher.ipynb   # Collect GitHub repository descriptions
├── RQ12.ipynb                         # Generate descriptions and evaluate results
├── data/
│   ├── lib_name.csv
│   ├── github_descriptions.csv
│   └── ...
└── README.md
```

---

## Installation

Install the required packages:

```bash
pip install openai pandas sentence-transformers scikit-learn python-dotenv
```

Create a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

---

## Reproducing the Experiments

1. Fetch GitHub repository descriptions:

```text
github_description_fetcher.ipynb
```

2. Run the experiments:

```text
RQ12.ipynb
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

* Library popularity has a stronger influence on semantic alignment than temperature.
* Middle-tier libraries achieve the highest semantic similarity.
* Temperature has only a small effect on generated content.

### RQ2

* AI-generated descriptions are generally longer than the original GitHub descriptions.
* Generated descriptions are also more linguistically complex according to the Gunning Fog Index.
* Readability varies across popularity tiers but remains relatively stable across temperature settings.

