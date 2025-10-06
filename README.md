# UK Vacancy Time-Series Analysis Across Vintages

## Overview
This repository presents a structured analysis of historical UK vacancy estimates published by the Office for National Statistics (ONS). The objective is to examine how vacancy figures evolve across successive data vintages and to forecast future vacancy levels using statistical modelling. The project encompasses:
- Automated data acquisition, 
- Data preparation and structuring, 
- Visualisation of revision patterns, 
- Time series forecasting with diagnostic evaluation. 

The analysis is designed to be modular, reproducible, and extensible, with all code written in Python and version-controlled for transparency.

## Repository Contents
- initial_script.py – First version of the analysis script with data ingestion, preparation, and model identification. 
- UK_Vacancies_Analysis.py – Final refactored script containing all classes and functions for data acquisition, processing, visualisation, and forecasting. 
- Notebook.ipynb – Working notebook used during development. 
- Technical_Appendix.pdf – Detailed documentation delineating methodology, findings, and forecasting approach. 
- Library_Requirements.txt – List of required Python packages for reproducibility. 

## Versioning
This repository contains two key commits: 
- **Initial version**: Full working script with ingestion, data preparation, and forecast model identification. 
- **Final version**: Refactored into classes, added interpretive chart, finalised forecasts and generated forecast visualisation with confidence intervals. 

## How to Obtain and Run Locally
The main script `UK_Vacancies_Analysis.py` is self-contained and automatically runs the full analysis. Simply execute the script to:
- Download historical CSV files, 
- Structure and consolidate the data, 
- Generate visualisations, 
- Produce forecasts with confidence intervals. 

## Manual Execution (Optional)
If you prefer to run each step manually or interact with individual components, you may use the following commands:

### 1. Clone the repository:
```bash
git clone https://github.com/LiviaExercises/UK-Vacancies-Time-Series-Analysis.git 
cd UK-Vacancies-Time-Series-Analysis
```
### 2. Install dependencies:
```bash
pip install -r Library_Requirements.txt
```
### 3. Run the analysis manually:
```python
from vacancy_analysis import VacanciesAcquisition, VacanciesStructuring, create_visualisations, forecast_vacancies

# Download data
vacancies = VacanciesAcquisition()
vacancies.download_csv_files(start=117, end=58, delay_seconds=3)

# Prepare data
unified = VacanciesStructuring()
all_data = unified.consolidate_all_data()

# Generate visualisations
create_visualisations(all_data)

# Run forecasts
forecast_df = forecast_vacancies(all_data, forecast_steps=6)
```

## Dependencies
The following Python libraries are required to run the notebook successfully:
- pandas
- requests
- plotly
- statsmodels

These are listed in `Library_Requirements.txt` for convenience.

## Technical Documentation
For a comprehensive explanation of the methodology, data handling procedures, visualisation strategy, and forecasting model, please refer to the Technical Appendix.
