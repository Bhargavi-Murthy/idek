import pandas as pd
import streamlit as st
import altair as alt

# App title and heading
st.set_page_config(page_title="Data Comparison App", layout="wide")
st.title("Dynamic Data Comparison Tool")
st.header("Upload two files to compare variable values across time periods.")

# Upload files
file1 = st.file_uploader("Upload the first file", type=["csv", "xlsx"])
file2 = st.file_uploader("Upload the second file", type=["csv", "xlsx"])

if file1 and file2:
    # Read files
    if file1.name.endswith(".csv"):
        df1 = pd.read_csv(file1)
    else:
        df1 = pd.read_excel(file1)

    if file2.name.endswith(".csv"):
        df2 = pd.read_csv(file2)
    else:
        df2 = pd.read_excel(file2)

    # Normalize column names
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()

    # Dropdown to select the ADS file
    st.sidebar.header("Select the ADS File")
    ads_selection = st.sidebar.radio("Choose the ADS File for Comparison", ["File 1", "File 2"])

    # Assign the selected ADS file to `ads_df`
    ads_df = df1 if ads_selection == "File 1" else df2

    # Ensure time column is named consistently
    time_column = "period"
    if time_column not in ads_df.columns:
        st.error(f"Column '{time_column}' must exist in the selected ADS file.")
    else:
        # Convert the period column to datetime
        ads_df[time_column] = pd.to_datetime(ads_df[time_column])

        # Allow users to select variables for comparison
        variable_columns = list(ads_df.columns)
        variable_columns.remove(time_column)  # Exclude the time column from selection

        selected_variable = st.sidebar.selectbox(
            "Select a variable for quarterly comparison:", variable_columns
        )

        if selected_variable:
            # Add date filters for two timeframes
            st.sidebar.subheader("Quarterly Comparison")
            with st.sidebar:
                st.subheader("Select Timeframe 1")
                start_date_1 = st.date_input("Start Date (Timeframe 1)", value=ads_df[time_column].min())
                end_date_1 = st.date_input("End Date (Timeframe 1)", value=ads_df[time_column].max())

                st.subheader("Select Timeframe 2")
                start_date_2 = st.date_input("Start Date (Timeframe 2)", value=ads_df[time_column].min())
                end_date_2 = st.date_input("End Date (Timeframe 2)", value=ads_df[time_column].max())

            # Filter data for both timeframes
            df_timeframe1 = ads_df[
                (ads_df[time_column] >= pd.Timestamp(start_date_1)) &
                (ads_df[time_column] <= pd.Timestamp(end_date_1))
            ]
            df_timeframe2 = ads_df[
                (ads_df[time_column] >= pd.Timestamp(start_date_2)) &
                (ads_df[time_column] <= pd.Timestamp(end_date_2))
            ]

            # Calculate total values for the selected variable in both timeframes
            total_timeframe1 = df_timeframe1[selected_variable].sum()
            total_timeframe2 = df_timeframe2[selected_variable].sum()

            # Compute change
            absolute_change = total_timeframe2 - total_timeframe1
            percentage_change = (absolute_change / total_timeframe1) * 100 if total_timeframe1 != 0 else None

            # Display results
            st.subheader("Quarterly Comparison Results")
            st.write(f"**Total for Timeframe 1 ({start_date_1} to {end_date_1}):** {total_timeframe1}")
            st.write(f"**Total for Timeframe 2 ({start_date_2} to {end_date_2}):** {total_timeframe2}")
            st.write(f"**Absolute Change:** {absolute_change}")
            st.write(f"**Percentage Change:** {percentage_change:.2f}%")

            # Visualization
            st.subheader("Quarterly Comparison Visualization")
            comparison_df = pd.DataFrame({
                "Timeframe": ["Timeframe 1", "Timeframe 2"],
                selected_variable: [total_timeframe1, total_timeframe2]
            })

            bar_chart = alt.Chart(comparison_df).mark_bar().encode(
                x="Timeframe",
                y=selected_variable,
                color="Timeframe",
                tooltip=[selected_variable]
            ).properties(
                title=f"Comparison of {selected_variable}",
                width=600,
                height=400
            )

            st.altair_chart(bar_chart, use_container_width=True)

        else:
            st.warning("Please select a variable for comparison.")
