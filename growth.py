# 📌 Data Sweeper - A Streamlit Project
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO

# 🏗️ Setup Streamlit App
st.set_page_config(page_title="💿 Data Sweeper Growth Mindset", layout="wide")
st.title("💿 Data Sweeper - Growth Mindset")
st.write("Upload CSV or Excel files, clean data, visualize results, and download the cleaned version.")

# 📂 File Uploader
uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True
)

# 📊 Process Each File
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # 🗂️ Read file into DataFrame
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine='openpyxl')
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"⚠️ Error loading {file.name}: {e}")
            continue

        # 📃 Display file info
        st.info(f"📂 **File Name:** {file.name} | 📏 **Size:** {file.size / 1024:.2f} KB")

        # 🔍 Preview DataFrame
        st.write("🔍 **Data Preview**")
        st.dataframe(df.head())

        # 🛠️ Data Cleaning Options
        st.subheader("🛠️ Data Cleaning")
        if st.checkbox(f"Enable cleaning for: {file.name}"):

            col1, col2 = st.columns(2)

            # 🚀 Remove Duplicates
            if col1.button(f"Remove Duplicates ({file.name})"):
                df.drop_duplicates(inplace=True)
                st.success("✅ Duplicates removed!")

            # 🏗️ Fill Missing Values
            if col2.button(f"Fill Missing Values ({file.name})"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("✅ Missing values filled!")

            # 🔍 Select Columns to Keep
            st.subheader("🎯 Select Columns to Keep")
            selected_columns = st.multiselect(f"Choose columns for {file.name}:", df.columns.tolist(), default=df.columns.tolist())
            df = df[selected_columns]

            # 📊 Data Visualization
            st.subheader("📊 Data Visualization")
            chart_type = st.selectbox("Choose chart type", ["Histogram", "Pie Chart"])

            if chart_type == "Histogram":
                numeric_column = st.selectbox("Select a numerical column for Histogram", df.select_dtypes(include=['number']).columns)
                if numeric_column:
                    st.bar_chart(df[numeric_column])  # Histogram using Streamlit

            elif chart_type == "Pie Chart":
                categorical_column = st.selectbox("Select a categorical column for Pie Chart", df.select_dtypes(include=['object']).columns)
                if categorical_column:
                    pie_data = df[categorical_column].value_counts()

                    # 🎨 Matplotlib Pie Chart
                    fig, ax = plt.subplots()
                    ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
                    ax.axis('equal')  # Ensures it’s a circle

                    st.pyplot(fig)  # Display Pie Chart in Streamlit

            # 📥 Download Cleaned File
            st.subheader("📥 Download Cleaned File")

            def convert_df(df, file_type):
                output = BytesIO()
                if file_type == "csv":
                    df.to_csv(output, index=False)
                elif file_type == "xlsx":
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name="Cleaned Data")
                output.seek(0)
                return output

            file_format = st.radio("Select file format:", ["CSV", "Excel"], horizontal=True)
            if st.button(f"Download {file_format} File"):
                file_data = convert_df(df, file_format.lower())
                st.download_button(
                    label=f"⬇️ Download {file_format} File",
                    data=file_data,
                    file_name=f"cleaned_{file.name}.{file_format.lower()}",
                    mime="text/csv" if file_format == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        st.write("---")  # Separator for multiple files
