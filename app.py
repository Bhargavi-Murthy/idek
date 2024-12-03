from dotenv import load_dotenv
import streamlit as st
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize Streamlit app
st.set_page_config(page_title="File Comparison")
st.header("Compare Two Files")

# File uploaders
file1 = st.file_uploader("Upload the first file", type=["csv", "xlsx"])
file2 = st.file_uploader("Upload the second file", type=["csv", "xlsx"])

if file1 and file2:
    # Read files into DataFrames
    if file1.name.endswith(".csv"):
        df1 = pd.read_csv(file1)
    else:
        df1 = pd.read_excel(file1)
    
    if file2.name.endswith(".csv"):
        df2 = pd.read_csv(file2)
    else:
        df2 = pd.read_excel(file2)

    # Display the uploaded files
    st.write("Preview of File 1:")
    st.dataframe(df1.head())
    st.write("Preview of File 2:")
    st.dataframe(df2.head())

    # Dropdowns to select variable and time period
    common_columns = set(df1.columns).intersection(set(df2.columns))
    time_column = st.selectbox("Select the time period column:", list(common_columns))
    variable_column = st.selectbox("Select the variable column:", list(common_columns))

    if time_column and variable_column:
        # Merge files on the selected columns
        merged_df = pd.merge(
            df1[[time_column, variable_column]],
            df2[[time_column, variable_column]],
            on=time_column,
            suffixes=('_file1', '_file2')
        )

        # Calculate differences
        merged_df["Difference"] = merged_df[f"{variable_column}_file1"] - merged_df[f"{variable_column}_file2"]

        # Display the comparison
        st.write("Comparison Results:")
        st.dataframe(merged_df)
        
        # Option to download the results
        csv = merged_df.to_csv(index=False)
        st.download_button(
            label="Download Comparison Results",
            data=csv,
            file_name="comparison_results.csv",
            mime="text/csv"
        )
