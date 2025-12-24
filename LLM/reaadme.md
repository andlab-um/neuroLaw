# Psychological Bases of Judicial Decisions in Humans and Large Language Models

This repository contains the code and data for the study:

**Psychological Bases of Justice: How Emotions Shape Human and AI Judicial Decisions**

The project conducts a multi-level comparison between human participants and large language models (LLMs) in judicial punishment tasks, integrating behavioral data, fMRI evidence, large-scale prompt-based experiments, and representational analyses of model hidden states.

---

## Overview

Judicial decision-making is traditionally assumed to be rational and impartial. However, extensive psychological and neurocognitive evidence shows that emotions, social roles, and temporal context systematically influence human punishment judgments.

Recent advances in large language models raise the question of whether LLMs can function as computational analogues of human judicial decision-makers. This project investigates:

- Whether LLMs replicate human punishment and emotional response patterns  
- Whether emotional modulation influences LLM punishment decisions  
- Whether apparent similarities between humans and LLMs reflect shared mechanisms or only surface-level behavioral convergence  

---

## Repository Structure

data/           # Human and LLM data (behavioral data, fMRI data, model outputs)
prompts/        # Prompt templates and controlled experimental manipulations
experiments/    # Scripts for running LLM experiments and human-aligned pipelines
analysis/       # Behavioral, textual (CoT), and representational analyses
visualization/  # Scripts for reproducing figures and plots used in the paper
results/        # Generated figures, tables, intermediate results, and logs
utils/          # Shared utility functions (data loading, prompt handling, statistics)

---

## Data

### Criminal Case Stimuli
- 27 anonymized real-world criminal cases  
- Balanced across misdemeanor, felony, and capital offenses  
- Matched for linguistic and structural properties  

### Human Data
- Behavioral punishment and emotion ratings  
- fMRI ROI time-series data  
- Data collected under second-party (SPP, victim) and third-party (TPP, judge) perspectives  

### LLM Data
- Model outputs under systematically controlled prompt conditions  
- Parsed punishment scores, emotion ratings, and chain-of-thought text  
- Hidden states extracted from transformer layers for representational analysis  

> **Note:** All personal or sensitive information has been removed. This repository complies with ethical and privacy requirements.

---

## Prompt Design

LLMs are instructed to adopt specific roles and contextual settings using structured prompts that manipulate:

- Role perspective (Second-Party vs. Third-Party)  
- Punishment delay (Immediate vs. Delayed)  
- Emotional activation (With vs. Without emotion cue)  
- Time pressure (Short / Long / No limit)  
- Age framing (20–60 years)  

All manipulations are instantiated purely through prompt design while keeping evidentiary content constant.

---

## Environment Setup

Install dependencies via:

```bash
pip install -r requirements.txt
```

or using Conda:

```bash
conda env create -f environment.yml
```




