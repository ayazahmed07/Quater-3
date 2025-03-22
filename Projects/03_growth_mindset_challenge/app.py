import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("DATA SWEEPER")
st.write("Transfrom your files between CSV and Excel formats with built in data cleaning and visualization")

if "dfs" not in st.session_state:
    st.session_state.dfs = {}


uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Load the file only once and store in session_state
        if file.name not in st.session_state.dfs:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
            st.session_state.dfs[file.name] = df
        else:
            df = st.session_state.dfs[file.name]

        # Display info about the file
        st.write(f"**File Nanme:** {file.name}")
        st.write(f"**File Size:** {file.size/1024}")

         #Show 5 rows of our df
        st.write("Preview the Head of the Dataframe")
        st.dataframe(df.head())

        #Options for Data Cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2, col3 = st.columns(3)

            with col1: 
                if st.button(f"Remove Duplicate from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include={"number"}).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean)
                    st.write("Missing Values have been Filled!") 

            with col3:
                if st.button(f"Remove blank columns for {file.name}"):
                    df.dropna(axis=1, how="all", inplace=True)
                    st.write("Blank Columns Removed!")

            st.session_state.dfs[file.name] = df


        # Chose Specific Columns to Keep or Convert
        st.subheader("Select Columns to Convert")
        # Use the current (possibly cleaned) columns
        current_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            f"Choose Columns for {file.name}", 
            current_columns, 
            default=current_columns
        )
        # Update the DataFrame with the selected columns
        df = df[selected_columns]
        st.session_state.dfs[file.name] = df


        #Create Some Visulizations
        st.subheader("Data Visulization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include="number").iloc[:,:2]) 

        # Convert the File -----> CSV to Excel
        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)  
        if st.button(f"Convert {file.name}"):
            df = st.session_state.dfs[file.name]
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False) 
                file_name = file.name.replace(file_ext, ".xlsx") 
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            #Download Button

            st.download_button(
            label=f"Downlaod {file.name} as {conversion_type}",
            data=buffer,
            file_name=file_name,
            mime=mime_type

        )


st.success("All files process")

     
            




    

   
