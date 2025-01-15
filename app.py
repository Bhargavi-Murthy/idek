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

    # Ensure time column is named consistently
    time_column = "period"
    if time_column not in df1.columns or time_column not in df2.columns:
        st.error(f"Both files must contain the column '{time_column}'.")
    else:
        # Convert the period column to datetime
        df1[time_column] = pd.to_datetime(df1[time_column])
        df2[time_column] = pd.to_datetime(df2[time_column])

        # Identify all variable columns excluding the time column
        variable_columns = [col for col in df1.columns if col != time_column]

        if not variable_columns:
            st.warning("No variables available for comparison.")
        else:
            # Merge the two files on the time column
            merged_df = pd.merge(
                df1[[time_column] + variable_columns],
                df2[[time_column] + variable_columns],
                on=time_column,
                suffixes=("_file1", "_file2")
            )

            # Compute absolute and percentage differences for each variable
            for var in variable_columns:
                merged_df[f"{var}_absolute_change"] = (
                    merged_df[f"{var}_file2"] - merged_df[f"{var}_file1"]
                )
                merged_df[f"{var}_percentage_change"] = (
                    merged_df[f"{var}_absolute_change"] / merged_df[f"{var}_file1"]
                ) * 100

            # Create a detailed table for differences
            difference_table = []
            for var in variable_columns:
                diff_df = merged_df[[time_column, f"{var}_file1", f"{var}_file2", f"{var}_absolute_change", f"{var}_percentage_change"]]
                diff_df.columns = [time_column, "Value (File 1)", "Value (File 2)", "Absolute Change", "Percentage Change"]
                diff_df["Variable"] = var
                difference_table.append(diff_df)

            # Combine all variable-specific differences into a single DataFrame
            difference_table_df = pd.concat(difference_table).sort_values(by=[time_column, "Variable"])

            # Display the table
            st.subheader("Comparison Table: Changes Between Files")
            st.dataframe(difference_table_df)

            # Allow download of the detailed difference table
            csv = difference_table_df.to_csv(index=False)
            st.download_button(
                label="Download Detailed Difference Table",
                data=csv,
                file_name="detailed_difference_table.csv",
                mime="text/csv"
            )

            # Visualization with a dropdown to select a variable
            st.subheader("Visualize Differences Between Files")
            selected_variable = st.selectbox(
                "Select a variable to visualize differences between files:", variable_columns
            )

            if selected_variable:
                chart_data = merged_df[[time_column, f"{selected_variable}_absolute_change"]].rename(
                    columns={f"{selected_variable}_absolute_change": "Absolute Change"}
                )

                # Line chart for absolute differences over time
                line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                    x=alt.X(time_column, title="Time Period"),
                    y=alt.Y("Absolute Change", title=f"Absolute Change in {selected_variable}"),
                    tooltip=["Absolute Change"]
                ).properties(
                    title=f"Difference in {selected_variable} Over Time Between Files",
                    width=700,
                    height=400
                )

                st.altair_chart(line_chart, use_container_width=True)
