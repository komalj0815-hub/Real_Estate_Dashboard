"""
Real Estate Investment Advisor
================================
Run with:  streamlit run app.py

Make sure india_housing_prices.csv is in the same folder as this file.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
import os

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────
# PAGE SETUP
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Real Estate Investment Advisor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────
# LOAD AND PREPARE DATA  (runs once, then stays cached)
# ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Put india_housing_prices.csv in the same folder as app.py
    csv_path = os.path.join(os.path.dirname(__file__), "india_housing_prices.csv")
    df = pd.read_csv(csv_path)

    # --- Feature Engineering ---
    # 1. Price per Sq Ft
    df["Price_per_SqFt"] = (df["Price_in_Lakhs"] / df["Size_in_SqFt"]).round(4)

    # 2. Future price after 5 years at 8% annual growth
    df["Future_Price_5Yrs"] = (df["Price_in_Lakhs"] * (1.08 ** 5)).round(2)

    # 3. Appreciation amount
    df["Appreciation_Amount"] = (df["Future_Price_5Yrs"] - df["Price_in_Lakhs"]).round(2)

    # 4. Number of amenities
    df["Amenities_Count"] = df["Amenities"].apply(
        lambda x: len(str(x).split(",")) if pd.notnull(x) else 0
    )

    # 5. Good Investment label
    #    Rule: price/sqft <= market median  AND  BHK >= 2  AND  Ready to Move
    median_ppsf = df["Price_per_SqFt"].median()
    df["Good_Investment"] = (
        (df["Price_per_SqFt"] <= median_ppsf) &
        (df["BHK"] >= 2) &
        (df["Availability_Status"] == "Ready_to_Move")
    ).astype(int)

    return df

df = load_data()


# ──────────────────────────────────────────────────────
# SIDEBAR  – navigation
# ──────────────────────────────────────────────────────
st.sidebar.title("🏠 Real Estate Advisor")
st.sidebar.markdown("---")

page = st.sidebar.radio("Go to:", [
    "🏠 Home",
    "📊 EDA Dashboard",
    "🔍 Property Filter",
    "💰 Investment Checker",
    "🔮 Price Forecaster",
])

st.sidebar.markdown("---")
st.sidebar.write("**Dataset Info**")
st.sidebar.metric("Total Properties",  f"{len(df):,}")
st.sidebar.metric("Cities",            df["City"].nunique())
st.sidebar.metric("States",            df["State"].nunique())
st.sidebar.metric("Good Investments",  f"{df['Good_Investment'].sum():,}")


# ══════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════
if page == "🏠 Home":

    st.title("🏠 Real Estate Investment Advisor")
    st.write("**India Housing Dataset — Predicting Property Profitability & Future Value**")
    st.markdown("---")

    # Top 4 numbers
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Properties",  f"{len(df):,}")
    c2.metric("Cities Covered",    df["City"].nunique())
    c3.metric("States Covered",    df["State"].nunique())
    c4.metric("Good Investments",  f"{df['Good_Investment'].sum():,}")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📌 About This Project")
        st.write("""
This app helps explore India's real estate market using data analysis.

**What you can do here:**
- 📊 Explore 20 data analysis charts (EDA Dashboard)
- 🔍 Filter and search properties
- 💰 Check if a property is a good investment
- 🔮 Forecast a property's price after 5 years

**How we decide a Good Investment:**
- Price per Sq Ft is at or below the market median
- The property has 2 or more bedrooms (BHK ≥ 2)
- The property is Ready to Move in
        """)

    with col_b:
        st.subheader("Property Types in Dataset")
        pt = df["Property_Type"].value_counts()
        fig = px.pie(
            values=pt.values, names=pt.index,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(height=300, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Availability Status")
        av = df["Availability_Status"].value_counts()
        fig = px.bar(
            x=av.index, y=av.values,
            labels={"x": "Status", "y": "Number of Properties"},
            color=av.index,
            color_discrete_sequence=["#4C72B0", "#55A868"]
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Furnished Status")
        fu = df["Furnished_Status"].value_counts()
        fig = px.pie(
            values=fu.values, names=fu.index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=300, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════
# PAGE 2 — EDA DASHBOARD
# ══════════════════════════════════════════════════════
elif page == "📊 EDA Dashboard":

    st.title("📊 Exploratory Data Analysis")
    st.write("20 questions answered through charts and graphs.")
    st.markdown("---")

    section = st.selectbox("Choose a section:", [
        "Q1–5:   Price & Size Analysis",
        "Q6–10:  Location Analysis",
        "Q11–15: Feature Relationships",
        "Q16–20: Ownership & Investment",
    ])

    # ── Q1–5 ──────────────────────────────────────────
    if section == "Q1–5:   Price & Size Analysis":

        # Q1
        st.subheader("Q1. What is the distribution of property prices?")
        fig = px.histogram(
            df, x="Price_in_Lakhs", nbins=60,
            labels={"Price_in_Lakhs": "Price (₹ Lakhs)"},
            color_discrete_sequence=["#4C72B0"]
        )
        fig.add_vline(x=df["Price_in_Lakhs"].mean(),   line_dash="dash", line_color="red",
                      annotation_text=f"Mean ₹{df['Price_in_Lakhs'].mean():.0f}L")
        fig.add_vline(x=df["Price_in_Lakhs"].median(), line_dash="dash", line_color="green",
                      annotation_text=f"Median ₹{df['Price_in_Lakhs'].median():.0f}L")
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"Most properties are priced between "
                f"₹{df['Price_in_Lakhs'].quantile(0.25):.0f}L and "
                f"₹{df['Price_in_Lakhs'].quantile(0.75):.0f}L.")
        st.divider()

        # Q2
        st.subheader("Q2. What is the distribution of property sizes?")
        fig = px.histogram(
            df, x="Size_in_SqFt", nbins=60,
            labels={"Size_in_SqFt": "Size (sq ft)"},
            color_discrete_sequence=["#55A868"]
        )
        fig.add_vline(x=df["Size_in_SqFt"].mean(), line_dash="dash", line_color="red",
                      annotation_text=f"Mean {df['Size_in_SqFt'].mean():.0f} sqft")
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"Average property size is {df['Size_in_SqFt'].mean():.0f} sq ft.")
        st.divider()

        # Q3
        st.subheader("Q3. Which property type has the highest price per sq ft?")
        fig = px.box(
            df, x="Property_Type", y="Price_per_SqFt",
            color="Property_Type",
            labels={"Price_per_SqFt": "Price per Sq Ft", "Property_Type": "Property Type"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        top_type = df.groupby("Property_Type")["Price_per_SqFt"].median().idxmax()
        st.info(f"**{top_type}** properties have the highest median price per sq ft.")
        st.divider()

        # Q4
        st.subheader("Q4. Does a bigger property mean a higher price?")
        sample = df.sample(3000, random_state=42)
        fig = px.scatter(
            sample, x="Size_in_SqFt", y="Price_in_Lakhs", color="BHK",
            labels={"Size_in_SqFt": "Size (sq ft)", "Price_in_Lakhs": "Price (₹ Lakhs)"},
            trendline="ols", opacity=0.5,
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)
        corr = df["Size_in_SqFt"].corr(df["Price_in_Lakhs"])
        st.info(f"Correlation between size and price = **{corr:.2f}**. "
                "Larger properties generally cost more.")
        st.divider()

        # Q5
        st.subheader("Q5. Are there any outliers in price and size?")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(df, y="Price_per_SqFt", title="Price per Sq Ft Outliers",
                         color_discrete_sequence=["#4C72B0"])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(df, y="Size_in_SqFt", title="Property Size Outliers",
                         color_discrete_sequence=["#55A868"])
            st.plotly_chart(fig, use_container_width=True)
        q1 = df["Price_per_SqFt"].quantile(0.25)
        q3 = df["Price_per_SqFt"].quantile(0.75)
        iqr = q3 - q1
        n_out = len(df[(df["Price_per_SqFt"] < q1 - 1.5*iqr) | (df["Price_per_SqFt"] > q3 + 1.5*iqr)])
        st.info(f"{n_out:,} properties ({n_out/len(df)*100:.1f}%) are price outliers based on the IQR method.")

    # ── Q6–10 ─────────────────────────────────────────
    elif section == "Q6–10:  Location Analysis":

        # Q6
        st.subheader("Q6. Which state has the highest average price per sq ft?")
        state_data = df.groupby("State")["Price_per_SqFt"].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(
            state_data, x="Price_per_SqFt", y="State", orientation="h",
            labels={"Price_per_SqFt": "Avg Price/SqFt", "State": ""},
            color="Price_per_SqFt", color_continuous_scale="Blues"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        top_state = state_data.sort_values("Price_per_SqFt", ascending=False).iloc[0]
        st.info(f"**{top_state['State']}** has the highest average price per sq ft.")
        st.divider()

        # Q7
        st.subheader("Q7. Which cities have the highest average property price? (Top 15)")
        city_data = df.groupby("City")["Price_in_Lakhs"].mean().sort_values(ascending=False).head(15).reset_index()
        fig = px.bar(
            city_data, x="City", y="Price_in_Lakhs",
            labels={"Price_in_Lakhs": "Avg Price (₹ Lakhs)"},
            color="Price_in_Lakhs", color_continuous_scale="Greens"
        )
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"**{city_data.iloc[0]['City']}** is the most expensive city "
                f"with an average of ₹{city_data.iloc[0]['Price_in_Lakhs']:.0f}L.")
        st.divider()

        # Q8
        st.subheader("Q8. Which localities have the oldest properties? (Top 20)")
        loc_age = df.groupby("Locality")["Age_of_Property"].median().sort_values(ascending=False).head(20).reset_index()
        fig = px.bar(
            loc_age, x="Age_of_Property", y="Locality", orientation="h",
            labels={"Age_of_Property": "Median Age (years)", "Locality": ""},
            color="Age_of_Property", color_continuous_scale="Oranges"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Q9
        st.subheader("Q9. What is the BHK distribution across top 8 cities?")
        top_cities = df["City"].value_counts().head(8).index.tolist()
        city_bhk = (
            df[df["City"].isin(top_cities)]
            .groupby(["City", "BHK"]).size()
            .reset_index(name="Count")
        )
        fig = px.bar(
            city_bhk, x="City", y="Count", color="BHK",
            barmode="stack", color_continuous_scale="Blues"
        )
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)
        st.info("3 BHK is the most common configuration across all major cities.")
        st.divider()

        # Q10
        st.subheader("Q10. How do prices change with age in the top 5 most expensive localities?")
        top_loc = df.groupby("Locality")["Price_in_Lakhs"].mean().sort_values(ascending=False).head(5).index
        loc_df  = df[df["Locality"].isin(top_loc)].sort_values("Age_of_Property")
        fig = px.line(
            loc_df, x="Age_of_Property", y="Price_in_Lakhs", color="Locality",
            labels={"Age_of_Property": "Property Age (years)", "Price_in_Lakhs": "Price (₹ Lakhs)"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Q11–15 ────────────────────────────────────────
    elif section == "Q11–15: Feature Relationships":

        # Q11
        st.subheader("Q11. How are all numeric features related to each other?")
        num_cols = ["Price_in_Lakhs", "Price_per_SqFt", "Size_in_SqFt", "BHK",
                    "Age_of_Property", "Nearby_Schools", "Nearby_Hospitals",
                    "Amenities_Count", "Future_Price_5Yrs"]
        corr = df[num_cols].corr()
        fig  = px.imshow(
            corr, text_auto=".2f",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.info("Values close to 1 = strong positive link. Values close to -1 = opposite relationship.")
        st.divider()

        # Q12
        st.subheader("Q12. Do more nearby schools lead to a higher price per sq ft?")
        school_df = df.groupby("Nearby_Schools")["Price_per_SqFt"].mean().reset_index()
        fig = px.bar(
            school_df, x="Nearby_Schools", y="Price_per_SqFt",
            labels={"Nearby_Schools": "Number of Nearby Schools", "Price_per_SqFt": "Avg Price/SqFt"},
            color_discrete_sequence=["#4C72B0"]
        )
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Q13
        st.subheader("Q13. Do more nearby hospitals lead to a higher price per sq ft?")
        hosp_df = df.groupby("Nearby_Hospitals")["Price_per_SqFt"].mean().reset_index()
        fig = px.bar(
            hosp_df, x="Nearby_Hospitals", y="Price_per_SqFt",
            labels={"Nearby_Hospitals": "Number of Nearby Hospitals", "Price_per_SqFt": "Avg Price/SqFt"},
            color_discrete_sequence=["#55A868"]
        )
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Q14
        st.subheader("Q14. Does furnished status affect the property price?")
        fig = px.box(
            df, x="Furnished_Status", y="Price_in_Lakhs",
            color="Furnished_Status",
            labels={"Price_in_Lakhs": "Price (₹ Lakhs)", "Furnished_Status": "Status"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        best = df.groupby("Furnished_Status")["Price_in_Lakhs"].median().idxmax()
        st.info(f"**{best}** properties have the highest median price.")
        st.divider()

        # Q15
        st.subheader("Q15. Does the direction a property faces affect its price per sq ft?")
        facing_df = df.groupby("Facing")["Price_per_SqFt"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(
            facing_df, x="Facing", y="Price_per_SqFt",
            labels={"Facing": "Direction", "Price_per_SqFt": "Avg Price/SqFt"},
            color="Facing",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"**{facing_df.iloc[0]['Facing']}-facing** properties have the highest average price per sq ft.")

    # ── Q16–20 ────────────────────────────────────────
    elif section == "Q16–20: Ownership & Investment":

        # Q16
        st.subheader("Q16. What percentage of properties belong to each owner type?")
        owner_df = df["Owner_Type"].value_counts().reset_index()
        owner_df.columns = ["Owner_Type", "Count"]
        fig = px.pie(
            owner_df, values="Count", names="Owner_Type",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Q17
        st.subheader("Q17. How many properties are Ready to Move vs Under Construction?")
        avail_df = df["Availability_Status"].value_counts().reset_index()
        avail_df.columns = ["Status", "Count"]
        fig = px.bar(
            avail_df, x="Status", y="Count",
            color="Status",
            color_discrete_sequence=["#4C72B0", "#55A868"],
            text="Count"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Q18
        st.subheader("Q18. Does having a parking space affect the property price?")
        fig = px.box(
            df, x="Parking_Space", y="Price_in_Lakhs",
            color="Parking_Space",
            labels={"Parking_Space": "Has Parking", "Price_in_Lakhs": "Price (₹ Lakhs)"},
            color_discrete_sequence=["#DD8452", "#4C72B0"]
        )
        st.plotly_chart(fig, use_container_width=True)
        p_yes = df[df["Parking_Space"] == "Yes"]["Price_in_Lakhs"].median()
        p_no  = df[df["Parking_Space"] == "No"]["Price_in_Lakhs"].median()
        st.info(f"Properties with parking have a median price ₹{abs(p_yes - p_no):.1f}L "
                f"{'higher' if p_yes > p_no else 'lower'} than those without.")
        st.divider()

        # Q19
        st.subheader("Q19. Do more amenities mean a higher price per sq ft?")
        amen_df = df.groupby("Amenities_Count")["Price_per_SqFt"].mean().reset_index()
        fig = px.line(
            amen_df, x="Amenities_Count", y="Price_per_SqFt",
            labels={"Amenities_Count": "Number of Amenities", "Price_per_SqFt": "Avg Price/SqFt"},
            markers=True, color_discrete_sequence=["#4C72B0"]
        )
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        # Q20
        st.subheader("Q20. Does public transport access affect property price?")
        transport_df = (
            df.groupby("Public_Transport_Accessibility")["Price_per_SqFt"]
            .mean().sort_values(ascending=False).reset_index()
        )
        fig = px.bar(
            transport_df, x="Public_Transport_Accessibility", y="Price_per_SqFt",
            labels={"Public_Transport_Accessibility": "Accessibility Level", "Price_per_SqFt": "Avg Price/SqFt"},
            color="Public_Transport_Accessibility",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"Areas with **{transport_df.iloc[0]['Public_Transport_Accessibility']}** "
                "transport access have the highest average price per sq ft.")


# ══════════════════════════════════════════════════════
# PAGE 3 — PROPERTY FILTER
# ══════════════════════════════════════════════════════
elif page == "🔍 Property Filter":

    st.title("🔍 Property Filter")
    st.write("Use the filters below to search for properties.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Location**")
        state_list = ["All"] + sorted(df["State"].unique().tolist())
        sel_state  = st.selectbox("State", state_list)

        if sel_state != "All":
            city_list = ["All"] + sorted(df[df["State"] == sel_state]["City"].unique().tolist())
        else:
            city_list = ["All"] + sorted(df["City"].unique().tolist())
        sel_city = st.selectbox("City", city_list)

    with col2:
        st.write("**Property Details**")
        type_list = ["All"] + sorted(df["Property_Type"].unique().tolist())
        sel_type  = st.selectbox("Property Type", type_list)

        bhk_list = ["All"] + sorted(df["BHK"].unique().tolist())
        sel_bhk  = st.selectbox("BHK", bhk_list)

    with col3:
        st.write("**Price & Size**")
        p_min = float(df["Price_in_Lakhs"].min())
        p_max = float(df["Price_in_Lakhs"].max())
        price_range = st.slider("Price (₹ Lakhs)", p_min, p_max, (p_min, p_max), step=5.0)

        s_min = float(df["Size_in_SqFt"].min())
        s_max = float(df["Size_in_SqFt"].max())
        size_range = st.slider("Size (Sq Ft)", s_min, s_max, (s_min, s_max), step=100.0)

    col4, col5 = st.columns(2)
    with col4:
        furn_list = ["All"] + sorted(df["Furnished_Status"].unique().tolist())
        sel_furn  = st.selectbox("Furnished Status", furn_list)
    with col5:
        avail_list = ["All"] + sorted(df["Availability_Status"].unique().tolist())
        sel_avail  = st.selectbox("Availability", avail_list)

    # Apply all filters
    result = df.copy()
    if sel_state != "All": result = result[result["State"]               == sel_state]
    if sel_city  != "All": result = result[result["City"]                == sel_city]
    if sel_type  != "All": result = result[result["Property_Type"]       == sel_type]
    if sel_bhk   != "All": result = result[result["BHK"]                == sel_bhk]
    if sel_furn  != "All": result = result[result["Furnished_Status"]    == sel_furn]
    if sel_avail != "All": result = result[result["Availability_Status"] == sel_avail]
    result = result[
        (result["Price_in_Lakhs"] >= price_range[0]) & (result["Price_in_Lakhs"] <= price_range[1]) &
        (result["Size_in_SqFt"]   >= size_range[0])  & (result["Size_in_SqFt"]   <= size_range[1])
    ]

    st.markdown("---")
    st.subheader(f"Results: {len(result):,} properties found")

    if len(result) == 0:
        st.warning("No properties match your filters. Try changing the criteria.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Average Price",    f"₹{result['Price_in_Lakhs'].mean():.1f}L")
        m2.metric("Average Size",     f"{result['Size_in_SqFt'].mean():.0f} sqft")
        m3.metric("Good Investments", f"{result['Good_Investment'].sum():,}")
        m4.metric("Avg Price/SqFt",   f"₹{result['Price_per_SqFt'].mean():.4f}L")

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.histogram(
                result, x="Price_in_Lakhs", nbins=40,
                title="Price Distribution (Filtered Results)",
                labels={"Price_in_Lakhs": "Price (₹ Lakhs)"},
                color_discrete_sequence=["#4C72B0"]
            )
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.box(
                result, x="Property_Type", y="Price_in_Lakhs",
                title="Price by Property Type (Filtered Results)",
                color="Property_Type",
                labels={"Price_in_Lakhs": "Price (₹ Lakhs)", "Property_Type": "Type"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

        show_cols = [
            "City", "Locality", "Property_Type", "BHK", "Size_in_SqFt",
            "Price_in_Lakhs", "Price_per_SqFt", "Furnished_Status",
            "Availability_Status", "Good_Investment", "Future_Price_5Yrs"
        ]
        st.write("Showing first 100 matching properties:")
        st.dataframe(result[show_cols].head(100), use_container_width=True, height=400)


# ══════════════════════════════════════════════════════
# PAGE 4 — INVESTMENT CHECKER
# ══════════════════════════════════════════════════════
elif page == "💰 Investment Checker":

    st.title("💰 Investment Checker")
    st.write("Enter any property's details below to find out if it is a good investment.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Location**")
        city_input  = st.selectbox("City", sorted(df["City"].unique().tolist()))
        avail_input = st.selectbox("Availability Status", ["Ready_to_Move", "Under_Construction"])

    with col2:
        st.write("**Property Details**")
        bhk_input   = st.slider("BHK (Number of Bedrooms)", 1, 5, 3)
        size_input  = st.number_input("Size (sq ft)", min_value=200, max_value=10000, value=1200, step=50)
        price_input = st.number_input("Price (₹ Lakhs)", min_value=10.0, max_value=500.0, value=150.0, step=5.0)

    with col3:
        st.write("**Features**")
        parking_input   = st.selectbox("Parking Space",            ["Yes", "No"])
        transport_input = st.selectbox("Transport Accessibility",   ["High", "Medium", "Low"])
        schools_input   = st.slider("Number of Nearby Schools", 0, 10, 3)

    st.markdown("---")

    if st.button("✅ Check Investment", type="primary", use_container_width=True):

        ppsf        = round(price_input / size_input, 4) if size_input > 0 else 0
        median_ppsf = df["Price_per_SqFt"].median()

        # The 3 investment rules
        rule1 = ppsf <= median_ppsf
        rule2 = bhk_input >= 2
        rule3 = avail_input == "Ready_to_Move"

        passed  = sum([rule1, rule2, rule3])
        is_good = passed == 3

        # Investment score out of 100
        score = 0
        score += 40 if ppsf <= median_ppsf * 0.75 else (25 if ppsf <= median_ppsf else max(0, 10))
        score += min(20, bhk_input * 5)
        score += {"High": 15, "Medium": 10, "Low": 5}[transport_input]
        score += min(15, schools_input * 2)
        score += 10 if parking_input == "Yes" else 0
        score  = min(100, score)

        # ── Result display ──────────────────
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            if is_good:
                st.success("✅  GOOD INVESTMENT — All 3 criteria passed!")
            else:
                st.warning(f"⚠️  MODERATE INVESTMENT — Only {passed} out of 3 criteria passed.")

            st.write(" ")
            st.write("**Criteria Breakdown:**")
            st.write(f"{'✅' if rule1 else '❌'}  Price per SqFt (₹{ppsf:.4f}L) is at or below market median (₹{median_ppsf:.4f}L)")
            st.write(f"{'✅' if rule2 else '❌'}  BHK is 2 or more  (yours: {bhk_input})")
            st.write(f"{'✅' if rule3 else '❌'}  Property is Ready to Move  (yours: {avail_input})")

        with col_r2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Investment Score (out of 100)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar":  {"color": "#2ecc71" if score >= 60 else "#f39c12" if score >= 40 else "#e74c3c"},
                    "steps": [
                        {"range": [0,  40], "color": "#fde8e8"},
                        {"range": [40, 70], "color": "#fef3cd"},
                        {"range": [70, 100], "color": "#d4edda"},
                    ],
                }
            ))
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Your Price/SqFt",    f"₹{ppsf:.4f}L")
        m2.metric("Market Median PpSF", f"₹{median_ppsf:.4f}L")
        m3.metric("Investment Score",   f"{score}/100")
        m4.metric("Verdict",            "Good ✅" if is_good else "Moderate ⚠️")

        st.markdown("---")
        city_avg = df[df["City"] == city_input]["Price_in_Lakhs"].mean()

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            compare_df = pd.DataFrame({
                "Category":        ["Your Property", f"{city_input} Average", "Market Median"],
                "Price (₹ Lakhs)": [price_input, city_avg, df["Price_in_Lakhs"].median()]
            })
            fig = px.bar(
                compare_df, x="Category", y="Price (₹ Lakhs)",
                title="Your Property vs Market Benchmarks",
                color="Category",
                color_discrete_sequence=["#4C72B0", "#95a5a6", "#2ecc71"]
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_e2:
            score_bd = {
                "Price":     40 if ppsf <= median_ppsf * 0.75 else (25 if ppsf <= median_ppsf else 10),
                "BHK":       min(20, bhk_input * 5),
                "Transport": {"High": 15, "Medium": 10, "Low": 5}[transport_input],
                "Schools":   min(15, schools_input * 2),
                "Parking":   10 if parking_input == "Yes" else 0,
            }
            fig = px.bar(
                x=list(score_bd.values()), y=list(score_bd.keys()),
                orientation="h",
                title="Score Breakdown by Factor",
                labels={"x": "Points Scored", "y": "Factor"},
                color_discrete_sequence=["#4C72B0"]
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════
# PAGE 5 — PRICE FORECASTER
# ══════════════════════════════════════════════════════
elif page == "🔮 Price Forecaster":

    st.title("🔮 Price Forecaster")
    st.write("Enter a property's current price and find out what it could be worth in the future.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Property Details**")
        current_price  = st.number_input("Current Price (₹ Lakhs)", min_value=10.0, max_value=500.0, value=200.0, step=5.0)
        city_fc        = st.selectbox("City (for market comparison)", sorted(df["City"].unique().tolist()))

    with col2:
        st.write("**Forecast Settings**")
        growth_rate    = st.slider("Annual Growth Rate (%)", min_value=2, max_value=20, value=8, step=1)
        forecast_years = st.slider("Number of Years to Forecast", min_value=1, max_value=20, value=5, step=1)
        st.write(f"Formula used:  ₹{current_price:.0f}L  ×  (1 + {growth_rate/100})  ^  {forecast_years} years")

    st.markdown("---")

    if st.button("🔮 Forecast Price", type="primary", use_container_width=True):

        future_price     = current_price * ((1 + growth_rate / 100) ** forecast_years)
        appreciation     = future_price - current_price
        appreciation_pct = (appreciation / current_price) * 100

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current Price",                        f"₹{current_price:.1f}L")
        m2.metric(f"Estimated Price After {forecast_years} Yrs", f"₹{future_price:.1f}L", delta=f"+₹{appreciation:.1f}L")
        m3.metric("Total Gain",                           f"₹{appreciation:.1f}L")
        m4.metric("Total Gain %",                         f"{appreciation_pct:.1f}%")

        st.markdown("---")
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            yrs  = list(range(0, forecast_years + 1))
            vals = [current_price * ((1 + growth_rate / 100) ** y) for y in yrs]
            growth_df = pd.DataFrame({
                "Year":            [f"Year {y}" for y in yrs],
                "Price (₹ Lakhs)": vals
            })
            fig = px.line(
                growth_df, x="Year", y="Price (₹ Lakhs)",
                title=f"Price Growth Over {forecast_years} Years",
                markers=True, color_discrete_sequence=["#4C72B0"]
            )
            fig.add_hline(y=current_price, line_dash="dash", line_color="red",
                          annotation_text="Current Price")
            st.plotly_chart(fig, use_container_width=True)

        with col_f2:
            rates  = [4, 6, 8, 10, 12, 15]
            rate_df = pd.DataFrame({
                "Growth Rate":       [f"{r}%" for r in rates],
                "Future Price (₹L)": [round(current_price * ((1 + r/100) ** forecast_years), 1) for r in rates]
            })
            fig = px.bar(
                rate_df, x="Growth Rate", y="Future Price (₹L)",
                title="What If — Price at Different Growth Rates",
                color_discrete_sequence=["#4C72B0"],
                text="Future Price (₹L)"
            )
            fig.update_traces(texttemplate="₹%{text}L", textposition="outside")
            fig.add_hline(y=future_price, line_dash="dash", line_color="red",
                          annotation_text=f"Your rate: {growth_rate}%")
            st.plotly_chart(fig, use_container_width=True)

        # Year-by-year table
        st.subheader("📋 Year-by-Year Forecast Table")
        rows = []
        for y in range(1, forecast_years + 1):
            p    = current_price * ((1 + growth_rate / 100) ** y)
            prev = current_price * ((1 + growth_rate / 100) ** (y - 1))
            rows.append({
                "Year":                   y,
                "Projected Price (₹L)":   round(p, 2),
                "Gain This Year (₹L)":    round(p - prev, 2),
                "Total Gain So Far (₹L)": round(p - current_price, 2),
                "Total Gain (%)":         round((p - current_price) / current_price * 100, 2),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # City comparison
        st.markdown("---")
        city_future_avg = df[df["City"] == city_fc]["Future_Price_5Yrs"].mean()
        your_5yr        = current_price * ((1 + growth_rate / 100) ** 5)
        st.write(f"**5-Year Comparison with {city_fc} market:**")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Your Property (5yr)",  f"₹{your_5yr:.1f}L")
        mc2.metric(f"{city_fc} Avg (5yr)", f"₹{city_future_avg:.1f}L")
        mc3.metric("Difference",           f"₹{your_5yr - city_future_avg:.1f}L",
                   delta="Above market avg" if your_5yr > city_future_avg else "Below market avg")
