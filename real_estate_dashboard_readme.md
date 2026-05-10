# 🏠 Real Estate Investment Advisor

### Predicting Property Profitability & Future Value Using Data Analytics

---

## 📌 Project Overview

The **Real Estate Investment Advisor** is an interactive web application built using Streamlit that helps users analyze real estate properties across India.

This project performs:
- 📊 Exploratory Data Analysis (EDA)
- 🔍 Property filtering & search
- 💰 Investment quality analysis
- 🔮 Future property price forecasting

The application uses a large housing dataset and interactive visualizations to help users make smarter real estate investment decisions.

---

## 🚀 Live App

🌐 Streamlit App:
https://realestatedashboard-gnwa3vvxhrujbthg6ff7mq.streamlit.app/

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `compressed_data.csv.gz` | Compressed housing dataset |
| `requirements.txt` | Required Python libraries |
| `README.md` | Project documentation |

---

## ⚙️ Features

### 🏠 Home Page
- Project overview
- Summary statistics
- Property type charts
- Market insights

### 📊 EDA Dashboard
Interactive analysis of:
- Property prices
- Property sizes
- Location trends
- Investment patterns
- Amenities impact
- Correlation analysis

### 🔍 Property Filter
Users can filter properties by:
- State
- City
- BHK
- Property type
- Furnishing status
- Price range
- Property size

### 💰 Investment Checker
Checks whether a property is a good investment based on:
- Price per Sq Ft
- BHK count
- Availability status

Also generates an investment score out of 100.

### 🔮 Price Forecaster
Forecasts future property prices using compound annual growth.

Formula used:

```text
Future Price = Current Price × (1 + r)^n
```

Where:
- `r` = annual growth rate
- `n` = number of years

---

## 📌 Investment Classification Rule

A property is labelled as a **Good Investment** if:

1. Price per Sq Ft ≤ Market Median
2. BHK ≥ 2
3. Availability Status = Ready_to_Move

---

## 🧰 Tech Stack

### Programming & Analysis
- Python
- pandas
- numpy
- scikit-learn

### Visualization
- plotly
- matplotlib
- seaborn

### Web Application
- Streamlit

### Dataset Format
- Compressed CSV (`.csv.gz`)

---

## ▶️ How to Run Locally

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Make Sure These Files Exist Together

```text
app.py
compressed_data.csv.gz
requirements.txt
```

### 3️⃣ Run the App

```bash
streamlit run app.py
```

### 4️⃣ Open in Browser

```text
http://localhost:8501
```

---

## 📊 Key Insights Generated

- Price distribution across cities and states
- Property size vs price relationship
- Best investment regions
- Impact of amenities on pricing
- Transport accessibility effects
- Future appreciation analysis

---

## 📈 Forecasting Method

Future property prices are estimated using compound growth assumptions.

Default assumptions:
- Annual Growth Rate = 8%
- Forecast Period = 5 Years

Both can be customized in the application.

---

## 🎯 Project Objective

The goal of this project is to:
- Analyze India's real estate market
- Identify profitable investment opportunities
- Provide interactive data exploration
- Support data-driven property decisions

---

## 👩‍💻 Developed Using

- Python
- Streamlit
- Plotly
- Pandas
- NumPy

