import pandas as pd
import streamlit as st
import altair as alt
import datetime as dt

# App title and heading
st.set_page_config(page_title="Data Comparison and Analysis Tool")
st.title("Dynamic Data Comparison and Analysis Tool")
st.header("Upload two files to compare and analyze variable values across time periods.")

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

    # Ensure time column is named consistently
    time_column = "period"
    if time_column not in df1.columns or time_column not in df2.columns:
        st.error(f"Column '{time_column}' must exist in both files.")
    else:
        # Convert Period column to datetime format
        df1[time_column] = pd.to_datetime(df1[time_column])
        df2[time_column] = pd.to_datetime(df2[time_column])

        # Identify common variable columns
        common_vars = set(df1.columns) & set(df2.columns) - {time_column}

        if not common_vars:
            st.error("No common variable columns found between the two files.")
        else:
            st.write(f"Common variables: {common_vars}")

            # Merge files on Period and common variables
            merged_df = pd.merge(
                df1[[time_column] + list(common_vars)],
                df2[[time_column] + list(common_vars)],
                on=time_column,
                suffixes=("_file1", "_file2")
            )

            # Calculate differences for each variable
            for var in common_vars:
                merged_df[f"{var}_difference"] = (
                    merged_df[f"{var}_file1"] - merged_df[f"{var}_file2"]
                )

            # Display comparison
            st.write("Comparison Results:")
            st.dataframe(merged_df)

            # Data Visualization
            st.subheader("Visualize Differences")
            variable_to_plot = st.selectbox(
                "Select a variable to visualize differences:", list(common_vars)
            )

            if variable_to_plot:
                chart_data = merged_df[[time_column, f"{variable_to_plot}_difference"]]
                chart_data = chart_data.rename(
                    columns={f"{variable_to_plot}_difference": "Difference"}
                )

                # Line chart using Altair
                line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                    x=alt.X(time_column, title="Time Period"),
                    y=alt.Y("Difference", title=f"{variable_to_plot} Difference"),
                    tooltip=["Difference"]
                ).properties(
                    title=f"Difference in {variable_to_plot} Over Time",
                    width=700,
                    height=400
                )

                st.altair_chart(line_chart, use_container_width=True)

            # Q&A Feature
            st.subheader("Ask Questions About the Data")
            question = st.text_input("Ask a question (e.g., Total share of HTS_PLY in Q1):")
            if question:
                # Identify the variable and time period from the question
                quarter_map = {"Q1": [1, 2, 3], "Q2": [4, 5, 6], "Q3": [7, 8, 9], "Q4": [10, 11, 12]}
                variable = None
                quarter = None

                for var in common_vars:
                    if var in question:
                        variable = var
                        break

                for q, months in quarter_map.items():
                    if q in question:
                        quarter = months
                        break

                if variable and quarter:
                    # Filter data for the quarter
                    quarter_data = merged_df[
                        merged_df[time_column].dt.month.isin(quarter)
                    ]
                    total_share = quarter_data[f"{variable}_file1"].sum()

                    st.write(f"Total share of **{variable}** in the selected quarter: **{total_share:.2f}**")
                else:
                    st.error("Could not identify the variable or quarter in the question. Please rephrase.")

            # Allow download of results
            csv = merged_df.to_csv(index=False)
            st.download_button(
                label="Download Comparison Results",
                data=csv,
                file_name="comparison_results.csv",
                mime="text/csv"
            )
