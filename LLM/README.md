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
└── github
    ├── data
    │   └── final_crime_data.csv
    ├── experiment
    │   ├── LLM-hidden-state
    │   │   ├── batch_csv_to_prompts.py
    │   │   └── run (1).py
    │   └── LLM_scripts
    │       ├── exp001_age20_NAN-reasoning_with_emotion_DeepSeek.py
    │       ├── exp002_age20_NAN-reasoning_with_emotion_Kimi.py
    │       ├── exp003_age20_NAN-reasoning_with_emotion_Qwen.py
    │       ├── exp004_age20_NAN-reasoning_without_emotion_DeepSeek.py
    │       ├── exp005_age20_NAN-reasoning_without_emotion_Kimi.py
    │       ├── exp006_age20_NAN-reasoning_without_emotion_Qwen.py
    │       ├── exp007_age20_long-term-reasoning_with_emotion_DeepSeek.py
    │       ├── exp008_age20_long-term-reasoning_with_emotion_Kimi.py
    │       ├...
    │       └── experiment_runner.py
    ├── prompt
    │   └── prompt.py
    └── visualization
        ├── behavior-llm
        │   ├── behavioral_data_analysis_human.ipynb
        │   ├── behavioral_data_analysis_llm.ipynb
        │   ├── llm_embedding_res_brain.ipynb
        │   └── llm_embedding_rsa.ipynb
        ├── brain
        │   ├── fmri_replicate.ipynb
        │   └── fmri_replicate2.ipynb
        └── text
            ├── calculate_sentiment_density.py
            ├── calculate_sentiment_scores.py
            ├── text_length_by_time_pressure.png
            ├── time_pressure_merged_severity.png
            ├── visualize_text_length_by_time_pressure.py
            └── visualize_time_pressure_by_severity_new.py


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

