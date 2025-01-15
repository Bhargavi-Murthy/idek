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
        df1[time_column] = pd.to_datetime(df1[time_column])
        df2[time_column] = pd.to_datetime(df2[time_column])

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

        # Identify all variables excluding the time column
        variable_columns = list(ads_df.columns)
        variable_columns.remove(time_column)

        if not variable_columns:
            st.warning("No variables available for comparison.")
        else:
            # Compute totals for all variables in both timeframes
            totals_timeframe1 = df_timeframe1[variable_columns].sum()
            totals_timeframe2 = df_timeframe2[variable_columns].sum()

            # Compute differences for all variables
            absolute_changes = totals_timeframe2 - totals_timeframe1
            percentage_changes = (
                (absolute_changes / totals_timeframe1) * 100
            ).replace([float('inf'), -float('inf')], None)  # Handle divide-by-zero cases

            # Combine results into a DataFrame for display
            comparison_results = pd.DataFrame({
                "Variable": variable_columns,
                "Total (Timeframe 1)": totals_timeframe1.values,
                "Total (Timeframe 2)": totals_timeframe2.values,
                "Absolute Change": absolute_changes.values,
                "Percentage Change (%)": percentage_changes.values
            })

            # Display results
            st.subheader("Quarterly Comparison Results")
            st.write(comparison_results)

            # Visualization with dropdown selection
            st.subheader("Visualize Differences Across Variables")
            selected_variable = st.selectbox(
                "Select a variable for visualization:", variable_columns
            )

            if selected_variable:
                # Prepare data for the selected variable
                comparison_df = pd.DataFrame({
                    "Timeframe": ["Timeframe 1", "Timeframe 2"],
                    "Total": [totals_timeframe1[selected_variable], totals_timeframe2[selected_variable]]
                })

                # Bar chart for the selected variable
                bar_chart = alt.Chart(comparison_df).mark_bar().encode(
                    x="Timeframe",
                    y="Total",
                    color="Timeframe",
                    tooltip=["Total"]
                ).properties(
                    title=f"Comparison of {selected_variable}",
                    width=600,
                    height=400
                )

                st.altair_chart(bar_chart, use_container_width=True)

            # Allow download of comparison results
            csv = comparison_results.to_csv(index=False)
            st.download_button(
                label="Download Comparison Results",
                data=csv,
                file_name="comparison_results.csv",
                mime="text/csv"
            )

        # **New Feature**: Compare both files across the selected timeframes
        st.subheader("Compare Two Files Across Timeframes")

        # Merge the two files on the time column
        merged_df = pd.merge(
            df1[[time_column] + variable_columns],
            df2[[time_column] + variable_columns],
            on=time_column,
            suffixes=("_file1", "_file2")
        )

        # Compute differences for each variable
        for var in variable_columns:
            merged_df[f"{var}_difference"] = (
                merged_df[f"{var}_file2"] - merged_df[f"{var}_file1"]
            )

        # Line chart for visualization of differences
        st.subheader("Visualize Differences Between Files")
        variable_for_line_chart = st.selectbox(
            "Select a variable to visualize differences between files:", variable_columns
        )

        if variable_for_line_chart:
            chart_data = merged_df[[time_column, f"{variable_for_line_chart}_difference"]].rename(
                columns={f"{variable_for_line_chart}_difference": "Difference"}
            )

            # Line chart for differences over time
            line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                x=alt.X(time_column, title="Time Period"),
                y=alt.Y("Difference", title=f"Difference in {variable_for_line_chart}"),
                tooltip=["Difference"]
            ).properties(
                title=f"Difference in {variable_for_line_chart} Over Time Between Files",
                width=700,
                height=400
            )

            st.altair_chart(line_chart, use_container_width=True)
