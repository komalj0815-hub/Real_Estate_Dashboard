"""
STREAMLIT APP: Real Estate Investment Advisor
=============================================
Run with:  streamlit run app.py

Features:
  1. 📊 EDA Dashboard  – All 20 interactive charts
  2. 🏠 Property Filter – Filter by area, price, BHK, city
  3. 💰 Investment Checker – Is this property a Good Investment?
  4. 🔮 Price Forecaster – Estimated price after 5 years
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Real Estate Investment Advisor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1f4e79;
        text-align: center;
        padding: 10px 0 5px 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 18px;
        color: white;
        text-align: center;
    }
    .good-invest {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .bad-invest {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        border-radius: 12px;
        padding: 20px;
        color: #333;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1f4e79;
        border-bottom: 2px solid #4C72B0;
        padding-bottom: 6px;
        margin-top: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("india_housing_cleaned.csv")
    except FileNotFoundError:
        # If running before preprocessing, load raw and apply minimal prep
        df = pd.read_csv("india_housing_prices.csv")
        df["Price_per_SqFt"] = df["Price_in_Lakhs"] / df["Size_in_SqFt"]
        GROWTH_RATE, YEARS = 0.08, 5
        df["Future_Price_5Yrs"] = (df["Price_in_Lakhs"] * ((1 + GROWTH_RATE) ** YEARS)).round(2)
        df["Appreciation_Amount"] = (df["Future_Price_5Yrs"] - df["Price_in_Lakhs"]).round(2)
        df["Appreciation_Rate_Pct"] = ((df["Appreciation_Amount"] / df["Price_in_Lakhs"]) * 100).round(2)
        df["Amenities_Count"] = df["Amenities"].apply(lambda x: len(str(x).split(",")) if pd.notnull(x) else 0)
        median_ppsf = df["Price_per_SqFt"].median()
        df["Good_Investment"] = ((df["Price_per_SqFt"] <= median_ppsf) & (df["BHK"] >= 2) & (df["Availability_Status"] == "Ready_to_Move")).astype(int)
        df["Age_Band"] = pd.cut(df["Age_of_Property"], bins=[0, 5, 15, 25, 100],
                                labels=["New (0-5 yrs)", "Mid (6-15 yrs)", "Old (16-25 yrs)", "Very Old (25+ yrs)"])
    return df

df = load_data()


# ─────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/home.png", width=70)
st.sidebar.markdown("## 🏠 Real Estate Advisor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Home", "📊 EDA Dashboard", "🔍 Property Filter", "💰 Investment Checker", "🔮 Price Forecaster"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset Overview**")
st.sidebar.metric("Total Properties", f"{len(df):,}")
st.sidebar.metric("Cities", df["City"].nunique())
st.sidebar.metric("States", df["State"].nunique())
st.sidebar.metric("Good Investments", f"{df['Good_Investment'].sum():,}")


# ═══════════════════════════════════════════════════════
# PAGE 1: HOME
# ═══════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="main-header">🏠 Real Estate Investment Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Predicting Property Profitability & Future Value | India Housing Dataset</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Properties", f"{len(df):,}")
    col2.metric("🏙️ Cities Covered", df["City"].nunique())
    col3.metric("📍 States Covered", df["State"].nunique())
    col4.metric("✅ Good Investments", f"{df['Good_Investment'].sum():,}")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 📌 Project Overview")
        st.markdown("""
        This application helps real estate investors make **data-driven decisions** by:

        - 🔍 **Exploring** India's housing market through 20 detailed EDA charts
        - 🏠 **Filtering** properties by city, BHK, price, and area
        - 💰 **Classifying** whether a property is a *Good Investment*
        - 🔮 **Forecasting** the estimated property price after **5 years**

        **Investment Rule Used:**
        > A property is classified as a *Good Investment* if:
        > - Price per Sq Ft ≤ Median Price per Sq Ft
        > - BHK ≥ 2
        > - Availability = Ready to Move
        """)

    with col_b:
        st.markdown("### 📊 Market Snapshot")
        # Pie of Property Types
        pt_counts = df["Property_Type"].value_counts()
        fig = px.pie(values=pt_counts.values, names=pt_counts.index,
                     title="Property Type Distribution",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=320, margin=dict(t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # Bottom row
    col_c, col_d = st.columns(2)
    with col_c:
        avail = df["Availability_Status"].value_counts()
        fig2 = px.bar(x=avail.index, y=avail.values, title="Availability Status",
                      labels={"x": "Status", "y": "Count"},
                      color=avail.index, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(height=320, showlegend=False, margin=dict(t=40, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col_d:
        furnished = df["Furnished_Status"].value_counts()
        fig3 = px.pie(values=furnished.values, names=furnished.index,
                      title="Furnished Status Distribution",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig3.update_layout(height=320, margin=dict(t=40, b=10))
        st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE 2: EDA DASHBOARD
# ═══════════════════════════════════════════════════════
elif page == "📊 EDA Dashboard":
    st.markdown('<div class="main-header">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">20 Analytical Questions Answered Through Visualizations</div>', unsafe_allow_html=True)
    st.markdown("---")

    eda_section = st.selectbox("Select EDA Section:", [
        "Q1–5: Price & Size Analysis",
        "Q6–10: Location-Based Analysis",
        "Q11–15: Feature Relationships & Correlation",
        "Q16–20: Investment / Amenities / Ownership"
    ])

    # ── Q1–5 ──────────────────────────────
    if eda_section == "Q1–5: Price & Size Analysis":
        st.markdown('<div class="section-title">Q1–5: Price & Size Analysis</div>', unsafe_allow_html=True)

        # Q1
        st.markdown("#### Q1. What is the distribution of property prices?")
        fig = px.histogram(df, x="Price_in_Lakhs", nbins=60, title="Distribution of Property Prices",
                           labels={"Price_in_Lakhs": "Price (₹ Lakhs)"},
                           color_discrete_sequence=["#4C72B0"])
        fig.add_vline(x=df["Price_in_Lakhs"].mean(), line_dash="dash", line_color="red",
                      annotation_text=f"Mean: ₹{df['Price_in_Lakhs'].mean():.1f}L")
        fig.add_vline(x=df["Price_in_Lakhs"].median(), line_dash="dash", line_color="green",
                      annotation_text=f"Median: ₹{df['Price_in_Lakhs'].median():.1f}L")
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"💡 **Insight:** Property prices range from ₹{df['Price_in_Lakhs'].min():.0f}L to ₹{df['Price_in_Lakhs'].max():.0f}L. "
                f"The mean (₹{df['Price_in_Lakhs'].mean():.1f}L) is slightly higher than the median (₹{df['Price_in_Lakhs'].median():.1f}L), "
                f"indicating a right-skewed distribution with some high-value properties.")

        st.divider()

        # Q2
        st.markdown("#### Q2. What is the distribution of property sizes?")
        fig = px.histogram(df, x="Size_in_SqFt", nbins=60, title="Distribution of Property Size",
                           labels={"Size_in_SqFt": "Size (sq ft)"},
                           color_discrete_sequence=["#55A868"])
        fig.add_vline(x=df["Size_in_SqFt"].mean(), line_dash="dash", line_color="red",
                      annotation_text=f"Mean: {df['Size_in_SqFt'].mean():.0f} sqft")
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"💡 **Insight:** Average property size is {df['Size_in_SqFt'].mean():.0f} sq ft. "
                f"Size ranges from {df['Size_in_SqFt'].min()} to {df['Size_in_SqFt'].max()} sq ft.")

        st.divider()

        # Q3
        st.markdown("#### Q3. How does price per sq ft vary by property type?")
        fig = px.box(df, x="Property_Type", y="Price_per_SqFt",
                     title="Price per Sq Ft by Property Type",
                     color="Property_Type",
                     labels={"Price_per_SqFt": "Price per Sq Ft (₹ Lakhs)", "Property_Type": "Property Type"},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
        top_type = df.groupby("Property_Type")["Price_per_SqFt"].median().idxmax()
        st.info(f"💡 **Insight:** **{top_type}** properties have the highest median price per sq ft.")

        st.divider()

        # Q4
        st.markdown("#### Q4. Is there a relationship between property size and price?")
        sample = df.sample(3000, random_state=42)
        fig = px.scatter(sample, x="Size_in_SqFt", y="Price_in_Lakhs", color="BHK",
                         title="Size vs Price (coloured by BHK)",
                         labels={"Size_in_SqFt": "Size (sq ft)", "Price_in_Lakhs": "Price (₹ Lakhs)"},
                         trendline="ols", opacity=0.5,
                         color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)
        corr_val = df["Size_in_SqFt"].corr(df["Price_in_Lakhs"])
        st.info(f"💡 **Insight:** Correlation between Size and Price = **{corr_val:.3f}**. "
                f"{'Moderate positive' if corr_val > 0.3 else 'Weak'} relationship — larger properties tend to cost more.")

        st.divider()

        # Q5
        st.markdown("#### Q5. Are there any outliers in price per sq ft or property size?")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(df, y="Price_per_SqFt", title="Outliers: Price per Sq Ft",
                         color_discrete_sequence=["#DD8452"])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(df, y="Size_in_SqFt", title="Outliers: Property Size",
                         color_discrete_sequence=["#4C72B0"])
            st.plotly_chart(fig, use_container_width=True)
        q1_p = df["Price_per_SqFt"].quantile(0.25)
        q3_p = df["Price_per_SqFt"].quantile(0.75)
        iqr_p = q3_p - q1_p
        outliers = df[(df["Price_per_SqFt"] < q1_p - 1.5 * iqr_p) | (df["Price_per_SqFt"] > q3_p + 1.5 * iqr_p)]
        st.info(f"💡 **Insight:** {len(outliers):,} properties ({len(outliers)/len(df)*100:.1f}%) are price-per-sqft outliers using the IQR method.")

    # ── Q6–10 ─────────────────────────────
    elif eda_section == "Q6–10: Location-Based Analysis":
        st.markdown('<div class="section-title">Q6–10: Location-Based Analysis</div>', unsafe_allow_html=True)

        # Q6
        st.markdown("#### Q6. What is the average price per sq ft by state?")
        state_data = df.groupby("State")["Price_per_SqFt"].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(state_data, x="Price_per_SqFt", y="State", orientation="h",
                     title="Average Price per Sq Ft by State",
                     labels={"Price_per_SqFt": "Avg Price/SqFt (₹L)", "State": ""},
                     color="Price_per_SqFt", color_continuous_scale="Blues")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        top_state = state_data.sort_values("Price_per_SqFt", ascending=False).iloc[0]
        st.info(f"💡 **Insight:** **{top_state['State']}** has the highest average price per sq ft at ₹{top_state['Price_per_SqFt']:.4f}L/sqft.")

        st.divider()

        # Q7
        st.markdown("#### Q7. What is the average property price by city? (Top 15)")
        city_data = df.groupby("City")["Price_in_Lakhs"].mean().sort_values(ascending=False).head(15).reset_index()
        fig = px.bar(city_data, x="City", y="Price_in_Lakhs",
                     title="Top 15 Cities by Average Property Price",
                     labels={"Price_in_Lakhs": "Avg Price (₹ Lakhs)"},
                     color="Price_in_Lakhs", color_continuous_scale="Greens")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"💡 **Insight:** **{city_data.iloc[0]['City']}** leads with an average price of ₹{city_data.iloc[0]['Price_in_Lakhs']:.1f}L.")

        st.divider()

        # Q8
        st.markdown("#### Q8. What is the median age of properties by locality? (Top 20)")
        loc_age = df.groupby("Locality")["Age_of_Property"].median().sort_values(ascending=False).head(20).reset_index()
        fig = px.bar(loc_age, x="Age_of_Property", y="Locality", orientation="h",
                     title="Top 20 Localities by Median Property Age",
                     labels={"Age_of_Property": "Median Age (yrs)", "Locality": ""},
                     color="Age_of_Property", color_continuous_scale="Oranges")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q9
        st.markdown("#### Q9. How is BHK distributed across cities?")
        top_cities = df["City"].value_counts().head(8).index.tolist()
        city_bhk = df[df["City"].isin(top_cities)].groupby(["City", "BHK"]).size().reset_index(name="Count")
        fig = px.bar(city_bhk, x="City", y="Count", color="BHK",
                     barmode="stack", title="BHK Distribution Across Top 8 Cities",
                     color_continuous_scale="Viridis")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q10
        st.markdown("#### Q10. Price trends for top 5 most expensive localities")
        top_loc = df.groupby("Locality")["Price_in_Lakhs"].mean().sort_values(ascending=False).head(5).index
        loc_df = df[df["Locality"].isin(top_loc)].sort_values("Age_of_Property")
        fig = px.line(loc_df, x="Age_of_Property", y="Price_in_Lakhs", color="Locality",
                      title="Price Trends for Top 5 Expensive Localities",
                      labels={"Age_of_Property": "Property Age (yrs)", "Price_in_Lakhs": "Price (₹L)"},
                      color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Insight:** This shows how property prices vary across age within the most expensive localities.")

    # ── Q11–15 ────────────────────────────
    elif eda_section == "Q11–15: Feature Relationships & Correlation":
        st.markdown('<div class="section-title">Q11–15: Feature Relationships & Correlation</div>', unsafe_allow_html=True)

        # Q11
        st.markdown("#### Q11. How are numeric features correlated with each other?")
        num_cols = ["Price_in_Lakhs", "Price_per_SqFt", "Size_in_SqFt", "BHK",
                    "Age_of_Property", "Nearby_Schools", "Nearby_Hospitals",
                    "Floor_No", "Total_Floors", "Amenities_Count", "Future_Price_5Yrs"]
        corr = df[num_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", title="Correlation Heatmap",
                        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                        aspect="auto")
        fig.update_layout(height=550)
        st.plotly_chart(fig, use_container_width=True)
        # Find strongest correlations
        corr_flat = corr.unstack().drop_duplicates().sort_values(ascending=False)
        corr_flat = corr_flat[corr_flat < 0.999]
        st.info(f"💡 **Insight:** Strongest correlation: {corr_flat.index[0][0]} & {corr_flat.index[0][1]} = {corr_flat.iloc[0]:.3f}. "
                f"**Price_in_Lakhs** and **Future_Price_5Yrs** are perfectly correlated (as future price is derived from current price).")

        st.divider()

        # Q12
        st.markdown("#### Q12. How do nearby schools relate to price per sq ft?")
        school_df = df.groupby("Nearby_Schools")["Price_per_SqFt"].mean().reset_index()
        fig = px.bar(school_df, x="Nearby_Schools", y="Price_per_SqFt",
                     title="Nearby Schools vs Avg Price per Sq Ft",
                     labels={"Nearby_Schools": "Number of Nearby Schools", "Price_per_SqFt": "Avg Price/SqFt (₹L)"},
                     color="Price_per_SqFt", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q13
        st.markdown("#### Q13. How do nearby hospitals relate to price per sq ft?")
        hosp_df = df.groupby("Nearby_Hospitals")["Price_per_SqFt"].mean().reset_index()
        fig = px.bar(hosp_df, x="Nearby_Hospitals", y="Price_per_SqFt",
                     title="Nearby Hospitals vs Avg Price per Sq Ft",
                     labels={"Nearby_Hospitals": "Number of Nearby Hospitals", "Price_per_SqFt": "Avg Price/SqFt (₹L)"},
                     color="Price_per_SqFt", color_continuous_scale="Greens")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q14
        st.markdown("#### Q14. How does price vary by furnished status?")
        fig = px.violin(df, x="Furnished_Status", y="Price_in_Lakhs",
                        title="Price Distribution by Furnished Status",
                        color="Furnished_Status", box=True,
                        labels={"Price_in_Lakhs": "Price (₹ Lakhs)", "Furnished_Status": "Status"},
                        color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
        furn_summary = df.groupby("Furnished_Status")["Price_in_Lakhs"].median().sort_values(ascending=False)
        st.info(f"💡 **Insight:** **{furn_summary.index[0]}** properties have the highest median price at ₹{furn_summary.iloc[0]:.1f}L.")

        st.divider()

        # Q15
        st.markdown("#### Q15. How does price per sq ft vary by facing direction?")
        facing_df = df.groupby("Facing")["Price_per_SqFt"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(facing_df, x="Facing", y="Price_per_SqFt",
                     title="Price per Sq Ft by Facing Direction",
                     labels={"Facing": "Direction", "Price_per_SqFt": "Avg Price/SqFt (₹L)"},
                     color="Facing", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        top_facing = facing_df.iloc[0]
        st.info(f"💡 **Insight:** **{top_facing['Facing']}-facing** properties command the highest price per sq ft.")

    # ── Q16–20 ────────────────────────────
    elif eda_section == "Q16–20: Investment / Amenities / Ownership":
        st.markdown('<div class="section-title">Q16–20: Investment / Amenities / Ownership</div>', unsafe_allow_html=True)

        # Q16
        st.markdown("#### Q16. How many properties belong to each owner type?")
        owner_df = df["Owner_Type"].value_counts().reset_index()
        owner_df.columns = ["Owner_Type", "Count"]
        fig = px.pie(owner_df, values="Count", names="Owner_Type",
                     title="Properties by Owner Type",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q17
        st.markdown("#### Q17. How many properties are under each availability status?")
        avail_df = df["Availability_Status"].value_counts().reset_index()
        avail_df.columns = ["Status", "Count"]
        fig = px.bar(avail_df, x="Status", y="Count",
                     title="Properties by Availability Status",
                     color="Status",
                     color_discrete_sequence=["#4C72B0", "#DD8452"],
                     text="Count")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q18
        st.markdown("#### Q18. Does parking space affect property price?")
        fig = px.box(df, x="Parking_Space", y="Price_in_Lakhs",
                     title="Parking Space vs Property Price",
                     color="Parking_Space",
                     labels={"Parking_Space": "Parking Available", "Price_in_Lakhs": "Price (₹ Lakhs)"},
                     color_discrete_sequence=["#e74c3c", "#2ecc71"])
        st.plotly_chart(fig, use_container_width=True)
        p_with = df[df["Parking_Space"] == "Yes"]["Price_in_Lakhs"].median()
        p_without = df[df["Parking_Space"] == "No"]["Price_in_Lakhs"].median()
        diff = p_with - p_without
        st.info(f"💡 **Insight:** Properties **with parking** have a median price ₹{diff:.1f}L "
                f"{'higher' if diff > 0 else 'lower'} than those without.")

        st.divider()

        # Q19
        st.markdown("#### Q19. How do amenities affect price per sq ft?")
        amen_df = df.groupby("Amenities_Count")["Price_per_SqFt"].mean().reset_index()
        fig = px.line(amen_df, x="Amenities_Count", y="Price_per_SqFt",
                      title="Number of Amenities vs Avg Price per Sq Ft",
                      labels={"Amenities_Count": "Number of Amenities", "Price_per_SqFt": "Avg Price/SqFt (₹L)"},
                      markers=True, color_discrete_sequence=["#4C72B0"])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(76,114,176,0.15)")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Q20
        st.markdown("#### Q20. How does public transport accessibility relate to price per sq ft?")
        transport_df = df.groupby("Public_Transport_Accessibility")["Price_per_SqFt"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(transport_df, x="Public_Transport_Accessibility", y="Price_per_SqFt",
                     title="Transport Accessibility vs Avg Price per Sq Ft",
                     labels={"Public_Transport_Accessibility": "Accessibility Level", "Price_per_SqFt": "Avg Price/SqFt (₹L)"},
                     color="Public_Transport_Accessibility",
                     color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)
        top_transport = transport_df.iloc[0]
        st.info(f"💡 **Insight:** Areas with **{top_transport['Public_Transport_Accessibility']}** transport accessibility have the highest average price per sq ft.")


# ═══════════════════════════════════════════════════════
# PAGE 3: PROPERTY FILTER
# ═══════════════════════════════════════════════════════
elif page == "🔍 Property Filter":
    st.markdown('<div class="main-header">🔍 Property Filter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search and filter properties by your preferences</div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📍 Location Filters**")
        states = ["All"] + sorted(df["State"].unique().tolist())
        selected_state = st.selectbox("State", states)

        if selected_state != "All":
            city_options = ["All"] + sorted(df[df["State"] == selected_state]["City"].unique().tolist())
        else:
            city_options = ["All"] + sorted(df["City"].unique().tolist())
        selected_city = st.selectbox("City", city_options)

    with col2:
        st.markdown("**🏠 Property Filters**")
        prop_types = ["All"] + df["Property_Type"].unique().tolist()
        selected_type = st.selectbox("Property Type", prop_types)

        bhk_options = ["All"] + sorted(df["BHK"].unique().tolist())
        selected_bhk = st.selectbox("BHK", bhk_options)

    with col3:
        st.markdown("**💰 Price & Size Filters**")
        price_min, price_max = float(df["Price_in_Lakhs"].min()), float(df["Price_in_Lakhs"].max())
        price_range = st.slider("Price Range (₹ Lakhs)", price_min, price_max, (price_min, price_max), step=5.0)

        size_min, size_max = float(df["Size_in_SqFt"].min()), float(df["Size_in_SqFt"].max())
        size_range = st.slider("Size Range (Sq Ft)", size_min, size_max, (size_min, size_max), step=50.0)

    col4, col5 = st.columns(2)
    with col4:
        furnished_opts = ["All"] + df["Furnished_Status"].unique().tolist()
        selected_furnished = st.selectbox("Furnished Status", furnished_opts)
    with col5:
        avail_opts = ["All"] + df["Availability_Status"].unique().tolist()
        selected_avail = st.selectbox("Availability Status", avail_opts)

    # Apply filters
    filtered = df.copy()
    if selected_state != "All":
        filtered = filtered[filtered["State"] == selected_state]
    if selected_city != "All":
        filtered = filtered[filtered["City"] == selected_city]
    if selected_type != "All":
        filtered = filtered[filtered["Property_Type"] == selected_type]
    if selected_bhk != "All":
        filtered = filtered[filtered["BHK"] == selected_bhk]
    if selected_furnished != "All":
        filtered = filtered[filtered["Furnished_Status"] == selected_furnished]
    if selected_avail != "All":
        filtered = filtered[filtered["Availability_Status"] == selected_avail]
    filtered = filtered[
        (filtered["Price_in_Lakhs"] >= price_range[0]) & (filtered["Price_in_Lakhs"] <= price_range[1]) &
        (filtered["Size_in_SqFt"] >= size_range[0]) & (filtered["Size_in_SqFt"] <= size_range[1])
    ]

    st.markdown("---")
    st.markdown(f"### 🏘️ {len(filtered):,} Properties Found")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Price", f"₹{filtered['Price_in_Lakhs'].mean():.1f}L" if len(filtered) > 0 else "—")
    m2.metric("Avg Size", f"{filtered['Size_in_SqFt'].mean():.0f} sqft" if len(filtered) > 0 else "—")
    m3.metric("Good Investments", f"{filtered['Good_Investment'].sum():,}" if len(filtered) > 0 else "—")
    m4.metric("Avg Price/SqFt", f"₹{filtered['Price_per_SqFt'].mean():.4f}L" if len(filtered) > 0 else "—")

    if len(filtered) > 0:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.histogram(filtered, x="Price_in_Lakhs", nbins=40,
                               title="Filtered: Price Distribution",
                               color_discrete_sequence=["#4C72B0"])
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.box(filtered, x="Property_Type", y="Price_in_Lakhs",
                         title="Filtered: Price by Property Type",
                         color="Property_Type",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)

        display_cols = ["City", "Locality", "Property_Type", "BHK", "Size_in_SqFt",
                        "Price_in_Lakhs", "Price_per_SqFt", "Furnished_Status",
                        "Availability_Status", "Good_Investment", "Future_Price_5Yrs"]
        st.dataframe(
            filtered[display_cols].head(100).style.format({
                "Price_in_Lakhs": "₹{:.2f}L",
                "Price_per_SqFt": "₹{:.4f}L",
                "Future_Price_5Yrs": "₹{:.2f}L"
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.warning("No properties match your filters. Please adjust the criteria.")


# ═══════════════════════════════════════════════════════
# PAGE 4: INVESTMENT CHECKER
# ═══════════════════════════════════════════════════════
elif page == "💰 Investment Checker":
    st.markdown('<div class="main-header">💰 Investment Checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enter property details to check if it\'s a Good Investment</div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📍 Location**")
        city_input = st.selectbox("City", sorted(df["City"].unique().tolist()), key="invest_city")
        prop_type_input = st.selectbox("Property Type", df["Property_Type"].unique().tolist(), key="invest_ptype")
        avail_input = st.selectbox("Availability Status", df["Availability_Status"].unique().tolist(), key="invest_avail")

    with col2:
        st.markdown("**🏠 Property Details**")
        bhk_input = st.slider("BHK", 1, 5, 3, key="invest_bhk")
        size_input = st.number_input("Size (sq ft)", min_value=200, max_value=10000, value=1200, step=50, key="invest_size")
        price_input = st.number_input("Price (₹ Lakhs)", min_value=10.0, max_value=500.0, value=150.0, step=5.0, key="invest_price")

    with col3:
        st.markdown("**🏗️ Amenities & Features**")
        furnished_input = st.selectbox("Furnished Status", df["Furnished_Status"].unique().tolist(), key="invest_furn")
        parking_input = st.selectbox("Parking Space", ["Yes", "No"], key="invest_parking")
        transport_input = st.selectbox("Transport Accessibility", ["High", "Medium", "Low"], key="invest_trans")
        schools_input = st.slider("Nearby Schools", 0, 10, 3, key="invest_schools")

    st.markdown("---")

    if st.button("🔍 Check Investment", type="primary", use_container_width=True):
        # Calculate
        ppsf = price_input / size_input if size_input > 0 else 0
        median_ppsf = df["Price_per_SqFt"].median()

        # Multi-factor investment check
        criteria = {
            "Price per SqFt ≤ Median": ppsf <= median_ppsf,
            "BHK ≥ 2": bhk_input >= 2,
            "Ready to Move": avail_input == "Ready_to_Move",
        }
        passed = sum(criteria.values())
        is_good = passed == 3

        # Score calculation (0-100)
        score = 0
        # Price score
        if ppsf <= median_ppsf * 0.75:
            score += 40
        elif ppsf <= median_ppsf:
            score += 25
        else:
            score += max(0, 25 - int((ppsf - median_ppsf) / median_ppsf * 50))
        # BHK score
        score += min(20, bhk_input * 5)
        # Transport score
        score += {"High": 15, "Medium": 10, "Low": 5}[transport_input]
        # Schools score
        score += min(15, schools_input * 2)
        # Parking
        score += 10 if parking_input == "Yes" else 0
        score = min(100, score)

        st.markdown("---")
        col_r1, col_r2 = st.columns([1, 1])

        with col_r1:
            if is_good:
                st.markdown(f"""
                <div class="good-invest">
                    ✅ GOOD INVESTMENT!<br>
                    <span style="font-size:1rem; font-weight:400">This property meets all investment criteria</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bad-invest">
                    ⚠️ MODERATE INVESTMENT<br>
                    <span style="font-size:1rem; font-weight:400">Passed {passed}/3 criteria — review before investing</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📋 Criteria Breakdown:**")
            for criterion, result in criteria.items():
                icon = "✅" if result else "❌"
                st.markdown(f"{icon} {criterion}")

        with col_r2:
            # Gauge chart for score
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                title={"text": "Investment Score", "font": {"size": 16}},
                delta={"reference": 50, "increasing": {"color": "#2ecc71"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2ecc71" if score >= 60 else "#f39c12" if score >= 40 else "#e74c3c"},
                    "steps": [
                        {"range": [0, 40], "color": "#fadbd8"},
                        {"range": [40, 70], "color": "#fdebd0"},
                        {"range": [70, 100], "color": "#d5f5e3"},
                    ],
                    "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 60}
                }
            ))
            fig.update_layout(height=280, margin=dict(t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price per SqFt", f"₹{ppsf:.4f}L")
        m2.metric("Market Median PpSF", f"₹{median_ppsf:.4f}L", delta=f"{'Below ✅' if ppsf <= median_ppsf else 'Above ❌'}")
        m3.metric("Investment Score", f"{score}/100")
        m4.metric("Verdict", "Good ✅" if is_good else "Moderate ⚠️")

        # Compare with city average
        city_avg = df[df["City"] == city_input]["Price_in_Lakhs"].mean()
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            comparison_data = {
                "Category": ["Your Property", f"{city_input} Avg", "Market Median"],
                "Price (₹ Lakhs)": [price_input, city_avg, df["Price_in_Lakhs"].median()]
            }
            fig = px.bar(comparison_data, x="Category", y="Price (₹ Lakhs)",
                         title="Your Property vs Market Benchmarks",
                         color="Category",
                         color_discrete_sequence=["#3498db", "#95a5a6", "#2ecc71"])
            st.plotly_chart(fig, use_container_width=True)
        with col_e2:
            # Feature importance-like breakdown
            feature_scores = {
                "Price Competitiveness": 40 if ppsf <= median_ppsf * 0.75 else 25 if ppsf <= median_ppsf else 10,
                "BHK Value": min(20, bhk_input * 5),
                "Transport Access": {"High": 15, "Medium": 10, "Low": 5}[transport_input],
                "School Proximity": min(15, schools_input * 2),
                "Parking Bonus": 10 if parking_input == "Yes" else 0
            }
            fig = px.bar(x=list(feature_scores.values()), y=list(feature_scores.keys()),
                         orientation="h",
                         title="Score Breakdown by Factor",
                         labels={"x": "Points", "y": "Factor"},
                         color=list(feature_scores.values()),
                         color_continuous_scale="Greens")
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# PAGE 5: PRICE FORECASTER
# ═══════════════════════════════════════════════════════
elif page == "🔮 Price Forecaster":
    st.markdown('<div class="main-header">🔮 Price Forecaster</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Estimate your property\'s value after 5 years</div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏠 Property Details**")
        current_price = st.number_input("Current Price (₹ Lakhs)", min_value=10.0, max_value=500.0, value=200.0, step=5.0)
        city_fc = st.selectbox("City", sorted(df["City"].unique().tolist()), key="fc_city")
        prop_type_fc = st.selectbox("Property Type", df["Property_Type"].unique().tolist(), key="fc_ptype")

    with col2:
        st.markdown("**⚙️ Forecast Settings**")
        growth_rate = st.slider("Annual Growth Rate (%)", min_value=2, max_value=20, value=8, step=1)
        forecast_years = st.slider("Forecast Period (Years)", min_value=1, max_value=20, value=5, step=1)
        st.markdown(f"""
        > **Fixed rate formula:**
        > Future Price = Current × (1 + r)^t
        > = ₹{current_price:.1f}L × (1 + {growth_rate/100:.2f})^{forecast_years}
        """)

    if st.button("🔮 Forecast Price", type="primary", use_container_width=True):
        future_price = current_price * ((1 + growth_rate / 100) ** forecast_years)
        appreciation = future_price - current_price
        appreciation_pct = (appreciation / current_price) * 100

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price", f"₹{current_price:.1f}L")
        m2.metric(f"Price After {forecast_years} Yrs", f"₹{future_price:.1f}L",
                  delta=f"+₹{appreciation:.1f}L")
        m3.metric("Total Appreciation", f"₹{appreciation:.1f}L")
        m4.metric("Appreciation %", f"{appreciation_pct:.1f}%")

        st.markdown("---")
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            # Year-by-year growth table
            years_list = list(range(0, forecast_years + 1))
            prices_list = [current_price * ((1 + growth_rate / 100) ** y) for y in years_list]
            growth_df = pd.DataFrame({"Year": [f"Year {y}" for y in years_list], "Price (₹ Lakhs)": prices_list})

            fig = px.line(growth_df, x="Year", y="Price (₹ Lakhs)",
                          title=f"Price Growth Over {forecast_years} Years",
                          markers=True, color_discrete_sequence=["#4C72B0"])
            fig.update_traces(fill="tozeroy", fillcolor="rgba(76,114,176,0.15)")
            fig.add_hline(y=current_price, line_dash="dash", line_color="red", annotation_text="Current Price")
            st.plotly_chart(fig, use_container_width=True)

        with col_f2:
            # Compare growth rates
            rates = [4, 6, 8, 10, 12, 15]
            future_prices_by_rate = {f"{r}%": current_price * ((1 + r / 100) ** forecast_years) for r in rates}
            rate_df = pd.DataFrame(list(future_prices_by_rate.items()), columns=["Growth Rate", f"Price After {forecast_years} Yrs (₹L)"])
            fig = px.bar(rate_df, x="Growth Rate", y=f"Price After {forecast_years} Yrs (₹L)",
                         title=f"Price at Different Growth Rates (After {forecast_years} Yrs)",
                         color=f"Price After {forecast_years} Yrs (₹L)",
                         color_continuous_scale="Blues",
                         text=f"Price After {forecast_years} Yrs (₹L)")
            fig.update_traces(texttemplate="₹%{text:.1f}L", textposition="outside")
            # Highlight selected rate
            fig.add_hline(y=future_price, line_dash="dash", line_color="red",
                          annotation_text=f"Your rate ({growth_rate}%)")
            st.plotly_chart(fig, use_container_width=True)

        # Year-by-year breakdown table
        st.markdown("#### 📋 Year-by-Year Price Forecast")
        breakdown = []
        for y in range(1, forecast_years + 1):
            p = current_price * ((1 + growth_rate / 100) ** y)
            prev = current_price * ((1 + growth_rate / 100) ** (y - 1))
            breakdown.append({
                "Year": y,
                "Projected Price (₹L)": round(p, 2),
                "Annual Gain (₹L)": round(p - prev, 2),
                "Cumulative Gain (₹L)": round(p - current_price, 2),
                "Cumulative Gain (%)": round((p - current_price) / current_price * 100, 2),
            })
        forecast_table = pd.DataFrame(breakdown)
        st.dataframe(
            forecast_table.style.format({
                "Projected Price (₹L)": "₹{:.2f}L",
                "Annual Gain (₹L)": "₹{:.2f}L",
                "Cumulative Gain (₹L)": "₹{:.2f}L",
                "Cumulative Gain (%)": "{:.2f}%",
            }).background_gradient(subset=["Projected Price (₹L)"], cmap="Blues"),
            use_container_width=True,
            hide_index=True
        )

        # Compare with city average future price
        city_future_avg = df[df["City"] == city_fc]["Future_Price_5Yrs"].mean()
        st.markdown("---")
        st.markdown(f"**Market Comparison for {city_fc}:**")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Your Property (5yr)", f"₹{current_price * ((1 + growth_rate/100)**5):.1f}L")
        mc2.metric(f"{city_fc} Avg (5yr forecast)", f"₹{city_future_avg:.1f}L")
        mc3.metric("Difference", f"₹{(current_price * ((1 + growth_rate/100)**5)) - city_future_avg:.1f}L",
                   delta="Above market avg" if (current_price * ((1 + growth_rate/100)**5)) > city_future_avg else "Below market avg")
