import streamlit as st
import pandas as pd
import os
import plotly.express as px
from io import BytesIO

# 🏗️ Streamlit App Setup
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")
st.title("💿 Data Sweeper - Growth Mindset")
st.write("Upload CSV or Excel files, clean data, and visualize results.")

# 📂 File Uploader
uploaded_files = st.file_uploader("Upload CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

# Store Data in Session State to Improve Performance
if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}

# 📊 Process Each File
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        try:
            # 🗂️ Read File
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine='openpyxl')
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue

            # Store in session state
            st.session_state.dataframes[file.name] = df

            # 📃 Display File Info
            st.info(f"📂 **File:** {file.name} | 📏 **Size:** {file.size / 1024:.2f} KB")
            
            # 🔍 Data Preview
            st.write("🔍 **Data Preview**")
            st.dataframe(df.head())
            
            # 🛠️ Data Cleaning Options
            st.subheader("🛠️ Data Cleaning")
            if st.checkbox(f"Enable cleaning for: {file.name}"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Remove Duplicates ({file.name})"):
                        df.drop_duplicates(inplace=True)
                        st.success("✅ Duplicates removed!")

                with col2:
                    if st.button(f"Fill Missing Values ({file.name})"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✅ Missing values filled!")
                
                # 🔍 Select Columns to Keep
                st.subheader("🎯 Select Columns to Keep")
                selected_columns = st.multiselect(f"Columns for {file.name}:", df.columns.tolist(), default=df.columns.tolist())
                df = df[selected_columns]

                # 📊 Data Visualization
                st.subheader("📊 Data Visualization")
                chart_type = st.selectbox("Choose chart type", ["Histogram", "Pie Chart", "Bar Chart"])
                
                if chart_type == "Histogram":
                    numeric_column = st.selectbox("Select a numerical column", df.select_dtypes(include=['number']).columns)
                    if numeric_column:
                        fig = px.histogram(df, x=numeric_column, title=f"Histogram of {numeric_column}")
                        st.plotly_chart(fig)

                elif chart_type == "Pie Chart":
                    categorical_column = st.selectbox("Select a categorical column", df.select_dtypes(include=['object']).columns)
                    if categorical_column:
                        fig = px.pie(df, names=categorical_column, title=f"Pie Chart of {categorical_column}")
                        st.plotly_chart(fig)
                
                elif chart_type == "Bar Chart":
                    numeric_column = st.selectbox("Select a numerical column for bar chart", df.select_dtypes(include=['number']).columns)
                    if numeric_column:
                        fig = px.bar(df, x=df.index, y=numeric_column, title=f"Bar Chart of {numeric_column}")
                        st.plotly_chart(fig)
                
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
        
        except Exception as e:
            st.error(f"⚠️ Error processing {file.name}: {e}")

        st.write("---")  # Separator for multiple files
