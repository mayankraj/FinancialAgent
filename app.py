import streamlit as st
import pandas as pd
from utils.data_parser import parse_statement
from utils.database import DatabaseManager
from utils.visualizations import create_equity_chart, create_metrics_chart
import io

# Page configuration
st.set_page_config(
    page_title="Financial Statement Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.title("Financial Statement Analyzer")
    
    # Initialize database
    db = DatabaseManager()
    
    # Sidebar
    st.sidebar.header("Upload Statement")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a financial statement file",
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file:
        try:
            # Show loading spinner
            with st.spinner('Processing your statement...'):
                # Read and parse the file
                file_content = uploaded_file.read()
                file_stream = io.BytesIO(file_content)
                
                # Parse the statement
                df = parse_statement(file_stream, uploaded_file.name)
                
                # Store in database
                db.store_statement_data(df, uploaded_file.name)
                
                # Display success message
                st.success("Statement processed successfully!")
                
                # Create dashboard
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Equity Exposure")
                    fig_equity = create_equity_chart(df)
                    st.plotly_chart(fig_equity, use_container_width=True)
                
                with col2:
                    st.subheader("Key Metrics")
                    fig_metrics = create_metrics_chart(df)
                    st.plotly_chart(fig_metrics, use_container_width=True)
                
                # Display raw data
                with st.expander("View Raw Data"):
                    st.dataframe(df)
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    else:
        # Display welcome message
        st.info("""
        👋 Welcome to the Financial Statement Analyzer!
        
        Upload your financial statement to:
        - Analyze equity exposure
        - View key metrics
        - Generate interactive visualizations
        
        Supported formats: CSV, Excel (xlsx, xls)
        """)

if __name__ == "__main__":
    main()
