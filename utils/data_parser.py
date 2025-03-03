import pandas as pd
import numpy as np

def parse_statement(file_stream, filename):
    """
    Parse financial statement data from various formats
    """
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_stream)
        else:
            df = pd.read_excel(file_stream)
        
        # Basic validation
        required_columns = ['Date', 'Amount', 'Category']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in the statement")
        
        # Clean and preprocess data
        df['Date'] = pd.to_datetime(df['Date'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # Calculate additional metrics
        df['equity_exposure'] = df.apply(calculate_equity_exposure, axis=1)
        df['risk_score'] = df.apply(calculate_risk_score, axis=1)
        
        return df
    
    except Exception as e:
        raise Exception(f"Error parsing file: {str(e)}")

def calculate_equity_exposure(row):
    """
    Calculate equity exposure for each transaction
    """
    if 'equity' in str(row['Category']).lower():
        return row['Amount']
    return 0

def calculate_risk_score(row):
    """
    Calculate risk score based on transaction parameters
    """
    base_score = 1.0
    if row['equity_exposure'] > 0:
        base_score *= 1.5
    return base_score
