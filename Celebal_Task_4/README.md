# Azure Data Factory Mini Project

## Overview

This mini project demonstrates the implementation of an end-to-end data ingestion pipeline using **Microsoft Azure Data Factory (ADF)** and **Azure Blob Storage**. The pipeline reads a CSV file from an input Blob Storage container, validates its metadata, and copies it to a destination container, showcasing the fundamental concepts of Azure data integration and orchestration.

---

## Problem Statement

Build a complete Azure Data Factory pipeline that:

- Reads a CSV file from Azure Blob Storage.
- Uses a Linked Service and Datasets for source and destination.
- Validates the source file metadata.
- Copies the file to a new location.
- Successfully executes the pipeline.

---

## Objectives

- Learn Azure Blob Storage fundamentals.
- Configure Azure Data Factory resources.
- Create Linked Services for Azure Storage.
- Build Source and Destination Datasets.
- Implement a Copy Data activity.
- Validate source file metadata using the Get Metadata activity.
- Execute and monitor Azure Data Factory pipelines.

---

## Architecture

```text
                Azure Blob Storage
             +-----------------------+
             |  input container      |
             | Sample-Superstore.csv |
             +----------+------------+
                        |
                        |
                        ▼
             Azure Data Factory
        +----------------------------+
        |   Get Metadata Activity    |
        |      (Validation)          |
        +-------------+--------------+
                      |
                      ▼
        +----------------------------+
        |     Copy Data Activity     |
        +-------------+--------------+
                      |
                      ▼
             Azure Blob Storage
        +----------------------------+
        |   output container         |
        | Copied_Superstore.csv      |
        +----------------------------+
```

---

## Azure Services Used

| Service | Purpose |
|----------|---------|
| Azure Resource Group | Resource management |
| Azure Storage Account | Blob Storage hosting |
| Azure Blob Storage | Source and destination storage |
| Azure Data Factory | Data orchestration |
| Linked Service | Storage connection |
| Dataset | Source and destination file definitions |
| Copy Data Activity | Data movement |
| Get Metadata Activity | Metadata validation |

---

## Project Workflow

1. Created an Azure Resource Group.
2. Created an Azure Storage Account.
3. Created two Blob Storage containers:
   - `input`
   - `output`
4. Uploaded `Sample-Superstore.csv` to the input container.
5. Created an Azure Data Factory instance.
6. Configured an Azure Blob Storage Linked Service.
7. Created:
   - Source Dataset
   - Destination Dataset
8. Built a Metadata Validation pipeline using the **Get Metadata** activity.
9. Built a Copy Data pipeline.
10. Combined both into a final Mini Project Pipeline.
11. Executed the pipeline successfully.
12. Verified the copied file in the output container.

---

## Project Structure

```text
Azure Resource Group
│
├── Azure Storage Account
│   ├── input
│   │     └── Sample-Superstore.csv
│   │
│   └── output
│         └── Copied_Superstore.csv
│
└── Azure Data Factory
    ├── Linked Service
    ├── Source Dataset
    ├── Destination Dataset
    ├── Metadata Pipeline
    ├── Copy Pipeline
    └── Mini Project Pipeline
```

---

## Pipeline Components

### Linked Service

Configured an Azure Blob Storage Linked Service to establish connectivity between Azure Data Factory and Azure Blob Storage.

---

### Source Dataset

- Type: Delimited Text (CSV)
- Container: `input`
- File: `Sample-Superstore.csv`

---

### Destination Dataset

- Type: Delimited Text (CSV)
- Container: `output`
- File: `Copied_Superstore.csv`

---

### Get Metadata Activity

Validated:

- File existence
- File size
- Last modified timestamp

---

### Copy Data Activity

Copied the source CSV file from the input container to the output container without modifying the data.

---

## Expected Output

- Source CSV successfully read from Blob Storage.
- Metadata validated successfully.
- Data copied to destination container.
- Pipeline executed successfully.

---

## Results

✔ Azure Storage configured successfully.

✔ Linked Service established successfully.

✔ Source and Destination Datasets created.

✔ Metadata validation completed successfully.

✔ Copy Data activity executed successfully.

✔ Output CSV generated in the destination container.

✔ Complete Azure Data Factory pipeline executed successfully.

---

## Learning Outcomes

This project provided practical experience with:

- Azure Resource Management
- Azure Blob Storage
- Azure Data Factory
- Linked Services
- Datasets
- Pipeline creation
- Metadata validation
- Copy Data activity
- Pipeline monitoring and debugging
- End-to-end cloud data integration

---

## Technologies Used

- Microsoft Azure
- Azure Data Factory (ADF)
- Azure Blob Storage
- CSV Dataset
- Azure Resource Manager

---

## Author

**Aditya Kumar**

B.Tech CSE (Cloud Computing)

Azure Data Factory Mini Project