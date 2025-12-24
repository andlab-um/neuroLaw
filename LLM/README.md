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

```project
│   README.md
│
├── data
│   │   README.md
│   │
│   ├── cases
│   │   │   raw_cases.json
│   │   │   anonymized_cases.json
│   │   │   case_metadata.csv
│   │
│   ├── human
│   │   │   behavioral_data.csv
│   │   │
│   │   └── fMRI
│   │       ├── preprocessed
│   │       │   ...
│   │       └── roi_timeseries
│   │           ...
│   │
│   └── llm
│       ├── raw_outputs
│       │   ...
│       ├── parsed_outputs
│       │   ...
│       └── hidden_states
│           ...
│
├── prompts
│   │   base_prompt.txt
│   │
│   ├── role_variants
│   │   │   judge_prompt.txt
│   │   │   victim_prompt.txt
│   │
│   ├── emotion_variants
│   │   │   with_emotion.txt
│   │   │   without_emotion.txt
│   │
│   ├── time_pressure_variants
│   │   │   short_time.txt
│   │   │   long_time.txt
│   │   │   no_limit.txt
│   │
│   └── full_prompt_templates
│       │   full_prompt_template.txt
│
├── experiments
│   │   run_llm_experiments.py
│   │   run_human_aligned_analysis.py
│   │   config.yaml
│
├── analysis
│   ├── behavioral
│   │   │   punishment_analysis.py
│   │   │   emotion_analysis.py
│   │   │   coupling_analysis.py
│   │
│   ├── text
│   │   │   cot_length_analysis.py
│   │   │   sentiment_lexicon_analysis.py
│   │   │   word_frequency.py
│   │
│   └── representation
│       │   extract_hidden_states.py
│       │   rsa_llm.py
│       │   rsa_brain_llm.py
│
├── visualization
│   │   plot_behavioral_results.py
│   │   plot_context_effects.py
│   │   plot_rsa_matrices.py
│   │   plot_figures_for_paper.py
│
├── results
│   ├── figures
│   │   ...
│   ├── tables
│   │   ...
│   └── logs
│       ...
│
└── utils
    │   data_utils.py
    │   prompt_utils.py
    │   llm_api_wrapper.py
    │   stats_utils.py

```

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

---

## Key Analyses
- Behavioral alignment and divergence between humans and LLMs
- Emotion–punishment coupling under role and delay conditions
- Prompt sensitivity and contextual modulation in LLMs
- Chain-of-thought textual and semantic analyses
- Hidden-state representational similarity analysis (RSA)
- Cross-modal comparison between LLM representations and human fMRI data

---

## Citation

If you use this code or data in your research, please cite the following paper:

```text
Kang, J., Zhang, S., Huang, J., Qi, Y., Wei, X., & Wu, H.
Psychological Bases of Justice: How Emotions Shape Human and AI Judicial Decisions.
```

