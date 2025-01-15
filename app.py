import pandas as pd

import streamlit as st

import altair as alt
 
# App title and heading

st.set_page_config(page_title="Data Comparison App", layout="wide")

st.title("Dynamic Data Comparison Tool")

st.header("Upload two files to compare variable values across time periods and geographies.")
 
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
 
    # Ensure required columns are present

    time_column = "period"

    geography_column = "geography"

    if time_column not in df1.columns or time_column not in df2.columns:

        st.error(f"Column '{time_column}' must exist in both files.")

    elif geography_column not in df1.columns or geography_column not in df2.columns:

        st.error(f"Column '{geography_column}' must exist in both files.")

    else:

        # Convert the period column to datetime

        df1[time_column] = pd.to_datetime(df1[time_column])

        df2[time_column] = pd.to_datetime(df2[time_column])
 
        # Identify common variable columns

        common_vars = set(df1.columns) & set(df2.columns) - {time_column, geography_column}
 
        if not common_vars:

            st.error("No common variable columns found between the two files.")

        else:

            st.write(f"Common variables: {common_vars}")
 
            # Merge files on Period, Geography, and common variables

            merged_df = pd.merge(

                df1[[time_column, geography_column] + list(common_vars)],

                df2[[time_column, geography_column] + list(common_vars)],

                on=[time_column, geography_column],

                suffixes=("_file1", "_file2")

            )
 
            # Add date filters for two timeframes

            st.sidebar.header("Quarterly Comparison")

            with st.sidebar:

                st.subheader("Select Timeframe 1")

                start_date_1 = st.date_input("Start Date (Timeframe 1)", value=df1[time_column].min())

                end_date_1 = st.date_input("End Date (Timeframe 1)", value=df1[time_column].max())
 
                st.subheader("Select Timeframe 2")

                start_date_2 = st.date_input("Start Date (Timeframe 2)", value=df2[time_column].min())

                end_date_2 = st.date_input("End Date (Timeframe 2)", value=df2[time_column].max())
 
            # Filter data for both timeframes

            df_timeframe1 = merged_df[

                (merged_df[time_column] >= pd.Timestamp(start_date_1)) &

                (merged_df[time_column] <= pd.Timestamp(end_date_1))

            ]

            df_timeframe2 = merged_df[

                (merged_df[time_column] >= pd.Timestamp(start_date_2)) &

                (merged_df[time_column] <= pd.Timestamp(end_date_2))

            ]
 
            # Select variable for comparison

            selected_variable = st.selectbox(

                "Select a variable for quarterly comparison:", list(common_vars)

            )
 
            if selected_variable:

                # Calculate total values for the selected variable in both timeframes

                total_timeframe1 = df_timeframe1[f"{selected_variable}_file1"].sum()

                total_timeframe2 = df_timeframe2[f"{selected_variable}_file2"].sum()
 
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
 
            # Calculate differences for each common variable

            for var in common_vars:

                merged_df[f"{var}_difference"] = (

                    merged_df[f"{var}_file1"] - merged_df[f"{var}_file2"]

                )
 
            # Display comparison results

            st.write("Comparison Results (All Variables):")

            st.dataframe(merged_df)
 
            # Data Visualization

            st.subheader("Visualize Differences Across All Variables")

            variable_to_plot = st.selectbox(

                "Select a variable to visualize differences:", list(common_vars)

            )
 
            if variable_to_plot:

                chart_data = merged_df[[time_column, geography_column, f"{variable_to_plot}_difference"]]

                chart_data = chart_data.rename(

                    columns={f"{variable_to_plot}_difference": "Difference"}

                )
 
                # Line chart using Altair

                line_chart = alt.Chart(chart_data).mark_line(point=True).encode(

                    x=alt.X(time_column, title="Time Period"),

                    y=alt.Y("Difference", title=f"{variable_to_plot} Difference"),

                    color=alt.Color(geography_column, title="Geography"),

                    tooltip=["Difference", geography_column]

                ).properties(

                    title=f"Difference in {variable_to_plot} Over Time by Geography",

                    width=700,

                    height=400

                )
 
                st.altair_chart(line_chart, use_container_width=True)
 
            # Allow download of comparison results

            csv = merged_df.to_csv(index=False)

            st.download_button(

                label="Download Comparison Results",

                data=csv,

                file_name="comparison_results.csv",

                mime="text/csv"

            )
 
