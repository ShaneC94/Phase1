# NGSIM Scenario Extraction – Phase 1

SOFE 4630U Cloud Computing Project

Group Members
- Bryan Parmar
- Riyan Faroqui
- Shane Currie

---

## Overview

This project builds a cloud-based monolithic pipeline for extracting driving scenarios from the NGSIM US-101 dataset.

The system processes vehicle trajectory data stored in Google Cloud Storage and extracts scenarios including:

- Car following
- Hard braking
- Lane changes

The pipeline is implemented using Apache Beam and executed on Google Cloud Dataflow.

---

## Architecture

NGSIM Dataset (TXT)
        │
        V
Google Cloud Storage
        │
        V
Apache Beam Pipeline (Dataflow)
        │
        ├ Data Cleaning
        ├ Segment Filtering
        ├ Scenario Detection
        └ Window Segmentation
        │
        V
BigQuery

---

## Setup

Install dependencies:

pip install -r requirements.txt

---

## Running the Pipeline

Upload dataset to GCS.

Then run:

python pipeline.py

---

## Output

Detected scenarios are stored in BigQuery:

dataset: ngsim_dataset
table: scenarios

---

## Scenario Visualization

Scenario outputs can be visualized using:

python visualization.py

This generates trajectory and velocity plots used to validate scenario detection.