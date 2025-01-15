import pandas as pd
import streamlit as st
import altair as alt
 
# App title and heading
st.set_page_config(page_title="Data Comparison App", layout="wide")
st.title("Dynamic Data Comparison Tool")
st.header("Upload data files and a period-to-quarter mapping file to compare variable values across time periods and geographies.")
 
# Upload files
file1 = st.file_uploader("Upload the first data file", type=["csv", "xlsx"])
file2 = st.file_uploader("Upload the second data file", type=["csv", "xlsx"])
mapping_file = st.file_uploader("Upload the period-to-quarter mapping file", type=["csv", "xlsx"])
 
if file1 and file2 and mapping_file:
    # Read files
    if file1.name.endswith(".csv"):
        df1 = pd.read_csv(file1)
    else:
        df1 = pd.read_excel(file1)
 
    if file2.name.endswith(".csv"):
        df2 = pd.read_csv(file2)
    else:
        df2 = pd.read_excel(file2)
 
    if mapping_file.name.endswith(".csv"):
        mapping_df = pd.read_csv(mapping_file)
    else:
        mapping_df = pd.read_excel(mapping_file)
 
    # Normalize column names
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()
    mapping_df.columns = mapping_df.columns.str.strip().str.lower()
 
    # Ensure required columns are present
    time_column = "period"
    geography_column = "geography"
    quarter_column = "quarter"
 
    if time_column not in df1.columns or time_column not in df2.columns:
        st.error(f"Column '{time_column}' must exist in both data files.")
    elif geography_column not in df1.columns or geography_column not in df2.columns:
        st.error(f"Column '{geography_column}' must exist in both data files.")
    elif time_column not in mapping_df.columns or quarter_column not in mapping_df.columns:
        st.error(f"Mapping file must contain columns '{time_column}' and '{quarter_column}'.")
    else:
        # Merge mapping file to associate periods with quarters
        df1 = pd.merge(df1, mapping_df, on=time_column, how="left")
        df2 = pd.merge(df2, mapping_df, on=time_column, how="left")
 
        # Check for missing quarters after the merge
        if df1[quarter_column].isnull().any() or df2[quarter_column].isnull().any():
            st.error("Some periods in the data files do not have corresponding quarters in the mapping file.")
        else:
            # Identify common variable columns
            common_vars = set(df1.columns) & set(df2.columns) - {time_column, geography_column, quarter_column}
 
            if not common_vars:
                st.error("No common variable columns found between the two files.")
            else:
                st.write(f"Common variables: {common_vars}")
 
                # Merge files on Quarter, Geography, and common variables
                merged_df = pd.merge(
                    df1[[quarter_column, geography_column] + list(common_vars)],
                    df2[[quarter_column, geography_column] + list(common_vars)],
                    on=[quarter_column, geography_column],
                    suffixes=("_file1", "_file2")
                )
 
                # Select quarter for comparison
                selected_quarters = st.multiselect(
                    "Select quarters for comparison:",
                    options=merged_df[quarter_column].unique(),
                    default=merged_df[quarter_column].unique()
                )
 
                if selected_quarters:
                    # Filter data for selected quarters
                    filtered_df = merged_df[merged_df[quarter_column].isin(selected_quarters)]
 
                    # Select variable for comparison
                    selected_variable = st.selectbox(
                        "Select a variable for comparison:", list(common_vars)
                    )
 
                    if selected_variable:
                        # Calculate total values for the selected variable by quarter
                        comparison_df = filtered_df.groupby(quarter_column).agg(
                            total_file1=(f"{selected_variable}_file1", "sum"),
                            total_file2=(f"{selected_variable}_file2", "sum")
                        ).reset_index()
 
                        # Add change calculations
                        comparison_df["absolute_change"] = comparison_df["total_file2"] - comparison_df["total_file1"]
                        comparison_df["percentage_change"] = (
                            (comparison_df["absolute_change"] / comparison_df["total_file1"]) * 100
                        ).replace([float("inf"), -float("inf")], None)
 
                        # Display results
                        st.subheader("Comparison Results by Quarter")
                        st.dataframe(comparison_df)
 
                        # Visualization
                        st.subheader("Comparison Visualization")
                        bar_chart = alt.Chart(comparison_df).mark_bar().encode(
                            x=alt.X(quarter_column, title="Quarter"),
                            y=alt.Y("total_file1", title="Total File 1"),
                            color=alt.value("blue"),
                            tooltip=[quarter_column, "total_file1", "total_file2", "absolute_change", "percentage_change"]
                        ).properties(
                            title=f"Comparison of {selected_variable} by Quarter",
                            width=700,
                            height=400
                        )
 
                        st.altair_chart(bar_chart, use_container_width=True)
 
                        # Allow download of comparison results
                        csv = comparison_df.to_csv(index=False)
                        st.download_button(
                            label="Download Comparison Results",
                            data=csv,
                            file_name="comparison_results_by_quarter.csv",
                            mime="text/csv"
                        )
                else:
                    st.error("Please select at least one quarter for comparison.")
