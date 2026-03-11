# US Unemployment Data Analysis (1990-2025)

## 📊 Overview
Analysis of unemployment trends across California, metro areas, and counties using PostgreSQL.

## 📁 Dataset
- **Source**: https://catalog.data.gov
- **Time Period**: 1990-2025
- **Key columns**: area_name, area_type, year, month, labor_force, employment, unemployment, unemployment_rate

## 🔍 Key Findings
- **Data Quality**: 63% of records have exact matches between labor_force and employment+unemployment
- **Highest Metro Rate**: Los Angeles-Long Beach-Glendale MD in 1990
- **Most Volatile**: Metropolitan Area shows highest unemployment variation

## 🗂️ Structure
🗂️ Structure
- `data/raw/unemployment.csv` - Raw unemployment data
- `scripts/unemploy_table.py` - Python script to load data
- `sql/unemployment_data_analysis.sql` - All SQL analysis queries
- `README.md` - Project documentation

## 💻 SQL Features
- Data validation, metro peaks, area trends

## 🚀 Quick Start
```bash
git clone https://github.com/liwuelaine/unemployment-analysis.git
cd unemployment-analysis
pip install -r requirements.txt
python scripts/unemploy_table.py
