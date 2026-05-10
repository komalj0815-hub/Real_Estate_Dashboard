# 🏠 Real Estate Investment Advisor
### Predicting Property Profitability & Future Value
---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `india_housing_prices.csv` | Raw dataset (you provide this) |
| `step1_preprocessing.py` | Data cleaning & feature engineering |
| `step2_eda.py` | All 20 EDA charts (saved as PNG) |
| `app.py` | Streamlit web application |
| `requirements.txt` | Python dependencies |

---

## 🚀 How to Run — Step by Step

### Step 1: Install Dependencies
Open your terminal / command prompt and run:
```bash
pip install -r requirements.txt
```

### Step 2: Place the Dataset
Make sure `india_housing_prices.csv` is in the **same folder** as all the scripts.

### Step 3: Run Preprocessing
```bash
python step1_preprocessing.py
```
This creates:
- `india_housing_cleaned.csv` — cleaned dataset with new features (used by Streamlit)
- `india_housing_encoded.csv` — encoded dataset ready for ML models

### Step 4: Run EDA (Optional — generates static charts)
```bash
python step2_eda.py
```
This creates an `eda_charts/` folder with 20 PNG chart files (one per EDA question).

### Step 5: Launch the Streamlit App
```bash
streamlit run app.py
```
Then open your browser at: **http://localhost:8501**

---

## 🗂️ What Each Step Does

### Step 1 — Data Preprocessing
- Loads the raw CSV (250,000 rows × 23 columns)
- Checks and removes duplicates
- Fills missing values (median for numbers, mode for categories)
- **Engineers new features:**
  - `Future_Price_5Yrs` — price after 5 years at 8% growth
  - `Appreciation_Amount` — gain in ₹ Lakhs
  - `Appreciation_Rate_Pct` — % gain
  - `School_Density_Score` — normalised schools score
  - `Hospital_Density_Score` — normalised hospitals score
  - `Amenities_Count` — number of amenities per property
  - `Age_Band` — property age category
  - `Good_Investment` — binary label (1 = good, 0 = not)
- Saves cleaned + encoded versions

### Step 2 — EDA (20 Questions)

**Q1–5: Price & Size Analysis**
- Q1: Distribution of property prices (histogram)
- Q2: Distribution of property sizes (histogram)
- Q3: Price per sq ft by property type (boxplot)
- Q4: Size vs price relationship (scatter + trendline)
- Q5: Outlier detection in price/size (boxplots)

**Q6–10: Location-Based Analysis**
- Q6: Avg price per sq ft by state (bar chart)
- Q7: Avg property price by city — top 15 (bar chart)
- Q8: Median property age by locality — top 20 (bar chart)
- Q9: BHK distribution across top 8 cities (stacked bar)
- Q10: Price trends for top 5 expensive localities (line chart)

**Q11–15: Feature Relationships & Correlation**
- Q11: Correlation heatmap of all numeric features
- Q12: Nearby schools vs price per sq ft
- Q13: Nearby hospitals vs price per sq ft
- Q14: Price distribution by furnished status (violin plot)
- Q15: Price per sq ft by facing direction

**Q16–20: Investment / Amenities / Ownership**
- Q16: Properties by owner type (pie chart)
- Q17: Properties by availability status (bar chart)
- Q18: Parking space effect on price (box plot)
- Q19: Amenities count vs price per sq ft (line chart)
- Q20: Transport accessibility vs price per sq ft (bar chart)

### Step 3 — Streamlit App (5 Pages)

| Page | What It Does |
|------|-------------|
| 🏠 Home | Summary stats, market overview charts |
| 📊 EDA Dashboard | All 20 EDA questions interactively |
| 🔍 Property Filter | Filter properties by city, price, BHK, etc. |
| 💰 Investment Checker | Enter property details → get Good/Bad verdict + score |
| 🔮 Price Forecaster | Enter price → get 5-year forecast with year-by-year table |

---

## 📌 Investment Classification Rule
A property is labelled **Good Investment = 1** if ALL of:
1. Price per Sq Ft ≤ Market Median Price per Sq Ft
2. BHK ≥ 2
3. Availability Status = Ready_to_Move

---

## 📌 Future Price Formula
```
Future Price = Current Price × (1 + 0.08)^5
```
Default annual growth rate = **8%**, forecast period = **5 years**
(Both can be adjusted in the Streamlit app)

---

## 🧰 Tech Stack
- **Python** — pandas, numpy, matplotlib, seaborn
- **Visualization** — plotly (interactive), matplotlib/seaborn (static EDA)
- **Web App** — Streamlit
- **Dataset** — India Housing Prices (250,000 records)
