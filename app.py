import pandas as pd
import streamlit as st

# Upload and read files
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

            # Allow download of results
            csv = merged_df.to_csv(index=False)
            st.download_button(
                label="Download Comparison Results",
                data=csv,
                file_name="comparison_results.csv",
                mime="text/csv"
            )
