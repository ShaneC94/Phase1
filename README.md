# NGSIM Scenario Extraction -- Phase 1

SOFE 4630U Cloud Computing Project

**Group Members** - Bryan Parmar - Riyan Faroqui - Shane Currie

------------------------------------------------------------------------

# Overview

This project builds a **cloud-based data processing pipeline** for
extracting driving scenarios from the **NGSIM US-101 vehicle trajectory
dataset**.

The system processes trajectory data stored in **Google Cloud Storage**
and identifies important driving scenarios including:

-   Car Following
-   Hard Braking
-   Lane Changes

The pipeline is implemented using **Apache Beam** and executed on
**Google Cloud Dataflow** for scalable distributed processing.

Detected scenarios are written to **Google BigQuery** for storage and
analysis.

------------------------------------------------------------------------

# Dataset

The NGSIM US-101 dataset contains detailed vehicle trajectory data
collected on the US-101 freeway in Los Angeles.

It includes:

-   Vehicle position
-   Velocity
-   Acceleration
-   Lane position
-   Surrounding vehicles

It can be downloaded at:

        https://data.transportation.gov/Automobiles/Next-Generation-Simulation-NGSIM-Vehicle-Trajector/8ect-6jqj/about_data

The file to download is named:

        US-101-LosAngeles-CA.zip

# Architecture

Pipeline stages:

        - Read NGSIM CSV (GCS)\
        - Parse Rows\
        - Remove Invalid Data\
        - Segment Filtering\
        - Scenario Detection\
        - Write Results to BigQuery

Cloud services used:

-   Google Cloud Storage -- dataset storage
-   Apache Beam -- pipeline definition
-   Google Cloud Dataflow -- distributed execution
-   BigQuery -- scenario storage and querying

------------------------------------------------------------------------

# Repository Structure

pipeline.py -- Apache Beam pipeline\
preprocessing.py -- CSV parsing and filtering logic\
scenarios.py -- Scenario detection logic\
visualization.py -- Scenario visualization scripts\
setup.py -- Package configuration for Dataflow workers

------------------------------------------------------------------------

# Setup

## 1. Install Dependencies

        pip install apache-beam[gcp]\
        pip install google-cloud-bigquery\
        pip install db-dtypes\
        pip install gcsfs\
        pip install matplotlib\
        pip install build

------------------------------------------------------------------------

## 2. Authenticate with Google Cloud

        gcloud auth login\
        gcloud auth application-default login

------------------------------------------------------------------------

## 3. Set Project

        gcloud config set project <PROJECT_ID>

Verify:

        gcloud config list

------------------------------------------------------------------------

# Running the Pipeline

## Define variables

        PROJECT=<PROJECT_ID>
        BUCKET=gs://<BUCKET_NAME>
        DATASET=<BQ_DATASET>
        TABLE=scenarios

Example:

        PROJECT=my-gcp-project
        BUCKET=gs://ngsim-dataflow-bucket
        DATASET=ngsim_dataset
        TABLE=scenarios

## 1. Create a Cloud Storage Bucket

        gsutil mb -l northamerica-northeast2 $BUCKET

### Dataflow Staging Folders

        gsutil mkdir $BUCKET/temp
        gsutil mkdir $BUCKET/staging

------------------------------------------------------------------------

## 2. Upload the NGSIM Dataset

        gsutil cp trajectories-0805am-0820am.csv $BUCKET

Verify:

        gsutil ls $BUCKET

------------------------------------------------------------------------

## 3. Create BigQuery Dataset

        bq --location=northamerica-northeast2 mk $DATASET

Verify:

        bq ls

The BigQuery table "scenarios" will automatically be created by the Apache Beam pipeline when ran.

------------------------------------------------------------------------

## 4. Run the Dataflow Pipeline
        
        python pipeline.py \
        --runner DataflowRunner \
        --project $PROJECT \
        --region northamerica-northeast2 \
        --worker_machine_type e2-small \
        --temp_location $BUCKET/temp \
        --staging_location $BUCKET/staging \
        --setup_file ./setup.py \
        --input $BUCKET/trajectories-0805am-0820am.csv \
        --output_table $PROJECT.$DATASET.$TABLE \
        --experiment use_unsupported_python_version

------------------------------------------------------------------------

# Monitoring the Pipeline

Open the **Dataflow dashboard** in the Google Cloud Console.

Expected stages:

        - Read NGSIM\
        - Parse Row\
        - Remove Invalid\
        - Segment Filter\
        - Detect Scenarios\
        - Write to BigQuery

------------------------------------------------------------------------

# Output

Detected scenarios are written to:

Example:

        BigQuery Dataset: ngsim_dataset\
        Table: scenarios

------------------------------------------------------------------------

# Scenario Visualization

Detected scenarios can be visualized using:

        python visualization.py

This generates trajectory and velocity plots used to validate scenario
detection. These are stored within plots/ and can be downloaded for viewing.

------------------------------------------------------------------------

# Notes

The NGSIM dataset records vehicle trajectories at **10 Hz**.

This means:

        50 frames ≈ 5 seconds

Scenario detection therefore operates on **5-second windows** of trajectory data.




