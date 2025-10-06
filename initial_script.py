# Step 1: Define a function to download 60 CSV files with delay between downloads (default), and create a directory to store the downloaded files (ensure no error is raised if the directory already exists). 

# Required Libraries: 
# - os: for directory creation and file path handling, 
# - requests: for sending HTTP requests to download data, 
# - time: for introducing delays between downloads. 

import os
import requests
import time

def download_csv_files(start=117, end=58, delay_seconds=3):
    os.makedirs("ONS_UK_Vacancies", exist_ok=True)
    for i in range(start, end - 1, -1):
        URL = f"https://www.ons.gov.uk/generator?format=csv&uri=/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/timeseries/ap2y/lms/previous/v{i}"
        # Construct the local file name for saving the file.
        filename = os.path.join("ONS_UK_Vacancies", f"v{i}.csv")
        try:
            # Send an HTTP GET request to the constructed URL.
            response = requests.get(URL)
            # Raise an error if the response status is not 200.
            response.raise_for_status()
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Download successful for v{i}")
        except Exception as e:
            print(f"Download failed for v{i}: {e}")
        time.sleep(delay_seconds) 


# Step 2: Define a function to extract vintage date from metadata. 

# Required Libraries: 
# - re: for regular expression matching to extract date patterns, 
# - pandas: for date parsing and handling missing time values. 

import re
import pandas as pd

def extract_vintage_date(filepath):
    try:
        # Open the file in read mode (‘r’) with UTF-8 encoding.
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if "Release date" in line:
                    match = re.search(r'\d{2}-\d{2}-\d{4}', line)
                    if match:
                        return pd.to_datetime(match.group(), format="%d-%m-%Y")
    except Exception as e:
        print(f"Error reading vintage from {filepath}: {e}")
    # Return NaT (Not a Time) from Pandas if no valid date is found or an error occurs.
    return pd.NaT 


# Step 3: Define a function to parse monthly series. 

# Required Libraries: 
# - pandas: for reading CSV files, parsing dates, and handling tabular data, 
# - re: for regular expression matching to identify valid date formats. 

import pandas as pd
import re

def parse_monthly_series(filepath):
    vintage = extract_vintage_date(filepath)
    try:
        df = pd.read_csv(filepath, header=None, names=["RawDate", "Value"],
                         encoding='utf-8')
        # Filter rows where the RawDate matches the pattern YYYY MMM, i.e. monthly series. 
        df = df[df["RawDate"].str.match(r"\d{4} [A-Z]{3}", na=False)]
        df["Date"] = pd.to_datetime(df["RawDate"].str.title(), format="%Y %b", errors="coerce")
        df["Value"] = pd.to_numeric(df["Value"].astype(str).str.replace('"', ''), errors="coerce")
        df["Vintage"] = vintage
        df = df.dropna(subset=["Date", "Value"])
        if not df.empty:
            df = df[["Date", "Value", "Vintage"]]
            print(f"Parsed {filepath}: {len(df)} monthly rows")
            return df
        else:
            print(f"No monthly data found in {filepath}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return pd.DataFrame() 


# Step 4: Define a function that performs aggregation of all the parsed datasets. 

# Required Libraries: 
# - os: for accessing the file system and constructing platform-independent paths, 
# - pandas: for data manipulation, aggregation, and export to CSV. 

import os
import pandas as pd

def consolidate_all_data():
    # Create an empty list to store individual DataFrames. 
    dataframes = []
    for file in os.listdir("ONS_UK_Vacancies"):
        # Construct the full path to each file (while ensuring platform-independence). 
        full_path = os.path.join("ONS_UK_Vacancies", file)
        # Call the previously defined function which returns a DataFrame containing filtered monthly time series data.
        df = parse_monthly_series(full_path)
        # Filter non-empty DataFrames.
        if not df.empty:
            dataframes.append(df)

    if dataframes:
        all_data = pd.concat(dataframes, ignore_index=True)
        print(f"\n Consolidated dataset contains {len(all_data)} rows across {len(dataframes)} vintages.")
        return all_data
    else:
        raise ValueError("No valid dataframes to concatenate.")

# Run all the functions.
download_csv_files(start=117, end=58, delay_seconds=3)
all_data = consolidate_all_data()
all_data = all_data.sort_values("Vintage").reset_index(drop=True)

# Create a readable month label.
all_data["MonthLabel"] = all_data["Date"].dt.strftime("%b %Y")

# Save the consolidated dataset to a CSV file.
all_data[["MonthLabel", "Value", "Vintage"]].to_csv("ONS_UK_Vacancies_Consolidated.csv", index=False, sep=";", encoding="utf-8") 


# Step 5: Create interactive line chart depicting how the estimate for e.g. February 2024 changed across vintages.

# Required Libraries: 
# - pandas: for date parsing and data filtering, 
# - plotly.express: for creating interactive line charts. 

import pandas as pd
import plotly.express as px

# Filter and prepare data.
selected_month = pd.to_datetime("2024-02-01")
selected_data = all_data[all_data["Date"] == selected_month].copy()
selected_data = selected_data.sort_values("Vintage")

# Create interactive line chart.
fig = px.line(
    selected_data,
    x="Vintage",
    y="Value",
    markers=True,
    title="Revisions of UK Vacancy Estimates for February 2024",
    labels={"Vintage": "Release Date (Vintage)", "Value": "Vacancy Estimate (Thousands)"}
)

fig.update_layout(
    title_font=dict(size=16, family="Trebuchet MS", color="black"),
    xaxis=dict(tickformat="%b %Y", tickangle=45),
    yaxis=dict(gridcolor="lightgray"),
    template="plotly_white"
)

fig.show()
# fig.write_html("vacancy_revisions_Feb2024.html") 


# Step 6 - A: Model identification. 

# Required Libraries: 
# - pandas: for time series manipulation and indexing, 
# - statsmodels: for conducting the Augmented Dickey-Fuller test to assess stationarity. 

import pandas as pd
from statsmodels.tsa.stattools import adfuller

# Prepare the finalised time series. 
latest_data = (
    all_data.sort_values("Vintage")
    .groupby("Date")
    .tail(1)
    .sort_values("Date")
)
ts = latest_data.set_index("Date")["Value"]
ts = ts.asfreq("MS") 

# Test for stationarity. 
from statsmodels.tsa.stattools import adfuller
result = adfuller(ts)
print(f"ADF Statistic: {result[0]}")
print(f"p-value: {result[1]}") 


# Step 6 - B: Model identification. 

# Required Libraries: 
# - statsmodels: for generating autocorrelation and partial autocorrelation plots, 
# - matplotlib: for rendering visualisations in a structured subplot layout. 

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt

# Apply first-order differencing to stabilise the series prior to ACF/PACF analysis. 
ts_diff = ts.diff().dropna()

# Generate ACF and PACF plots to assess serial dependence and guide model selection. 
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(ts_diff, lags=20, ax=axes[0])
plot_pacf(ts_diff, lags=20, ax=axes[1])
axes[0].set_title("ACF (Differenced Series)")
axes[1].set_title("PACF (Differenced Series)")
plt.tight_layout()
plt.show() 


# Step 7 - A: Model estimation. 

# Required Libraries: 
# - statsmodels: for specifying and fitting ARIMA models to time series data. 

from statsmodels.tsa.arima.model import ARIMA

# Fit an ARIMA(1,1,0) model to the finalised time series.
model = ARIMA(ts, order=(1, 1, 0))
fitted = model.fit(cov_type="approx")
print(fitted.summary()) 


# Step 7 - B: Model estimation. 

# Required Library: 
# - statsmodels: for specifying and fitting ARIMA models to time series data. 

from statsmodels.tsa.arima.model import ARIMA

# Fit an ARIMA(1,1,1) model to the finalised time series.
model = ARIMA(ts, order=(1, 1, 1))
fitted = model.fit(cov_type="approx")
print(fitted.summary()) 


# Step 8: Generate forecasts. 

# Generate a 6-month forecast using the fitted ARIMA model. 
forecast = fitted.forecast(steps=6)
print("Six-month forecast summary:")
print(forecast)