import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Dashboard title
st.title("🌾 Crop Yield and Weather Analysis - India")
st.write(
    "Interactive dashboard to analyze crop yield, "
    "rainfall, and climate patterns across Indian districts (1984-2017)."
)

# Upload dataset
uploaded_file = st.file_uploader(
    "Upload All-India District-wise Crop and Climate Dataset (CSV)",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.write("Total Records:", len(df))

    # Select dataset columns
    st.sidebar.header("Select Dataset Columns")

    columns = df.columns.tolist()

    def find_column(keywords):
        for col in columns:
            if any(word in col.lower() for word in keywords):
                return col
        return columns[0]

    district_col = st.sidebar.selectbox(
        "District Column",
        columns,
        index=columns.index(find_column(["district"]))
    )

    state_col = st.sidebar.selectbox(
        "State Column",
        columns,
        index=columns.index(find_column(["state"]))
    )

    crop_col = st.sidebar.selectbox(
        "Crop Column",
        columns,
        index=columns.index(find_column(["crop"]))
    )

    year_col = st.sidebar.selectbox(
        "Year Column",
        columns,
        index=columns.index(find_column(["year"]))
    )

    yield_col = st.sidebar.selectbox(
        "Crop Yield / Production Column",
        columns,
        index=columns.index(find_column(["yield"]))
    )

    # Weather columns are optional
    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if not numeric_cols:
        st.error("No numeric columns found in the dataset.")
        st.stop()

    weather_options = ["None"] + numeric_cols

    rainfall_col = st.sidebar.selectbox(
        "Rainfall Column (optional)",
        weather_options,
        index=next(
            (i for i, c in enumerate(weather_options)
             if "rain" in c.lower()), 0
        )
    )

    temperature_col = st.sidebar.selectbox(
        "Temperature Column (optional)",
        weather_options,
        index=next(
            (i for i, c in enumerate(weather_options)
             if "temp" in c.lower()), 0
        )
    )

    # Convert selected numeric fields
    df[year_col] = pd.to_numeric(
        df[year_col], errors="coerce"
    )
    df[yield_col] = pd.to_numeric(
        df[yield_col], errors="coerce"
    )

    if rainfall_col != "None":
        df[rainfall_col] = pd.to_numeric(
            df[rainfall_col], errors="coerce"
        )

    if temperature_col != "None":
        df[temperature_col] = pd.to_numeric(
            df[temperature_col], errors="coerce"
        )

    # Sidebar filters
    st.sidebar.header("Filter Data")

    states = ["All"] + sorted(
        df[state_col].dropna().astype(str).unique().tolist()
    )
    selected_state = st.sidebar.selectbox(
        "Select State", states
    )

    filtered = df.copy()

    if selected_state != "All":
        filtered = filtered[
            filtered[state_col].astype(str) == selected_state
        ]

    districts = ["All"] + sorted(
        filtered[district_col].dropna().astype(str).unique().tolist()
    )
    selected_district = st.sidebar.selectbox(
        "Select District", districts
    )

    if selected_district != "All":
        filtered = filtered[
            filtered[district_col].astype(str) == selected_district
        ]

    crops = ["All"] + sorted(
        filtered[crop_col].dropna().astype(str).unique().tolist()
    )
    selected_crop = st.sidebar.selectbox(
        "Select Crop", crops
    )

    if selected_crop != "All":
        filtered = filtered[
            filtered[crop_col].astype(str) == selected_crop
        ]

    # Summary statistics
    st.subheader("📊 Summary Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Records",
        len(filtered)
    )

    col2.metric(
        "Average Crop Yield / Value",
        round(filtered[yield_col].mean(), 2)
        if filtered[yield_col].notna().any()
        else "N/A"
    )

    col3.metric(
        "Number of Districts",
        filtered[district_col].nunique()
    )

    # Crop yield trend
    st.subheader("📈 Crop Yield Trend by Year")

    trend_data = filtered.dropna(
        subset=[year_col, yield_col]
    )

    if not trend_data.empty:
        yearly = trend_data.groupby(
            year_col
        )[yield_col].mean()

        fig, ax = plt.subplots()
        ax.plot(
            yearly.index, yearly.values,
            marker="o"
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Crop Yield / Value")
        ax.set_title("Year-wise Crop Trend")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No valid year and yield data available.")

    # District comparison
    st.subheader("📍 District-wise Crop Comparison")

    district_data = filtered.groupby(
        district_col
    )[yield_col].mean().sort_values(
        ascending=False
    ).head(10)

    if not district_data.empty:
        st.bar_chart(district_data)

    # Rainfall analysis
    if rainfall_col != "None":
        st.subheader("🌧️ Rainfall Analysis")

        weather_data = filtered.dropna(
            subset=[rainfall_col, yield_col]
        )

        if not weather_data.empty:
            fig, ax = plt.subplots()
            ax.scatter(
                weather_data[rainfall_col],
                weather_data[yield_col],
                alpha=0.6
            )
            ax.set_xlabel("Rainfall")
            ax.set_ylabel("Crop Yield / Value")
            ax.set_title("Rainfall vs Crop Yield")
            st.pyplot(fig)
            plt.close(fig)

            corr = weather_data[
                [rainfall_col, yield_col]
            ].corr().iloc[0, 1]

            st.write(
                "Rainfall-Yield Correlation:",
                round(corr, 3)
                if pd.notna(corr) else "N/A"
            )

    # Temperature analysis
    if temperature_col != "None":
        st.subheader("🌡️ Temperature Analysis")

        temp_data = filtered.dropna(
            subset=[temperature_col, yield_col]
        )

        if not temp_data.empty:
            fig, ax = plt.subplots()
            ax.scatter(
                temp_data[temperature_col],
                temp_data[yield_col],
                alpha=0.6
            )
            ax.set_xlabel("Temperature")
            ax.set_ylabel("Crop Yield / Value")
            ax.set_title("Temperature vs Crop Yield")
            st.pyplot(fig)
            plt.close(fig)

    # Final filtered dataset
    st.subheader("Filtered Agricultural Data")
    st.dataframe(filtered)

    # Download filtered data
    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Filtered Dataset",
        data=csv,
        file_name="filtered_crop_weather_data.csv",
        mime="text/csv"
    )

else:
    st.info(
        "Please upload your district-wise crop and climate "
        "dataset in CSV format to begin analysis."
    )
