# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data analysis project tracking a group of 1,024 people attempting to drink 1 million beers collectively. All beers are logged in a WhatsApp group chat, and this project analyzes the chat data to track progress and forecast completion dates.

## Environment Setup

This is a Python project using a virtual environment. To set up:

```bash
# Activate virtual environment 
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Common Commands

### Data Analysis and Forecasting
```bash
# Run the main forecast update script (processes latest WhatsApp data)
python scripts/update_linear_forecast.py

# Run Jupyter notebooks (requires jupyter to be installed)
jupyter notebook parse_whatsapp_chat.ipynb
jupyter notebook rate_of_beers.ipynb
jupyter notebook lurkers.ipynb
```

### Python Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install new packages
pip install <package_name>
pip freeze > requirements.txt
```

## Architecture

### Core Data Pipeline
1. **WhatsApp Chat Import** (`src/whatsapp_parser.py`): 
   - Loads WhatsApp chat exports from Google Cloud Storage
   - Parses chat messages using regex patterns
   - Extracts timestamps, senders, and beer counts from messages

2. **Data Cleaning** (`src/data_cleaning.py`):
   - Flags errors in beer counts (too high/low values)
   - Identifies statistical outliers using linear regression
   - Creates clean datasets for forecasting

3. **Visualization** (`src/plotting.py`):
   - Creates interactive Plotly charts showing beer consumption over time
   - Highlights weekends and outliers
   - Generates both HTML and PNG outputs

4. **Automated Updates** (`scripts/update_linear_forecast.py`):
   - Automatically finds the most recent WhatsApp chat file
   - Runs the complete data pipeline
   - Updates forecast plots and README content

### Key Data Flow
- Raw WhatsApp chat data → Parse messages → Clean data → Linear regression analysis → Generate forecasts and plots

### Google Cloud Integration
- Uses Google Cloud Storage to fetch WhatsApp chat exports
- Requires proper GCP credentials and access to the '1-million-beers' bucket
- Environment variables loaded via python-dotenv

### Output Files
- `beer_counts_with_outliers.png/html`: Raw data with outliers highlighted
- `beer_counts_with_linear_forecast.png/html`: Clean data with linear trend line
- `content_forecast.txt`: Text summary of current progress and forecasts

## Data Structure

The main DataFrame contains:
- `datetime`: Parsed timestamp from WhatsApp messages
- `n_beers`: Extracted beer count from messages
- `error`: Classification of data quality ('none', 'outlier', 'high', 'low')
- `flag`: Message type ('contains number', 'added', 'removed', 'other')

## Dependencies

Key packages:
- `pandas`, `numpy`: Data manipulation
- `plotly`: Interactive visualizations  
- `scikit-learn`: Linear regression modeling
- `google-cloud-storage`: GCP integration
- `jupyter`: Notebook environment for analysis