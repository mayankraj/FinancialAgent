import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
import re

def parse_pdf(file_stream):
    """
    Extract tabular data from PDF file
    """
    try:
        # Create PDF reader object
        pdf = PdfReader(file_stream)

        # Extract text from all pages
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

        # Simple parsing logic - looks for common patterns in financial statements
        # This is a basic implementation - can be enhanced based on specific PDF formats
        data = []

        # Split into lines and process
        lines = text.split('\n')
        for line in lines:
            # Look for lines with date and amount patterns
            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}', line)
            amount_match = re.search(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?', line)

            if date_match and amount_match:
                date = date_match.group(0)
                amount = float(amount_match.group(0).replace('$', '').replace(',', ''))
                category = 'Unclassified'  # Default category

                # Try to determine category based on keywords
                if any(keyword in line.lower() for keyword in ['stock', 'equity', 'share']):
                    category = 'Equity'
                elif any(keyword in line.lower() for keyword in ['bond', 'fixed income']):
                    category = 'Fixed Income'

                data.append({
                    'Date': date,
                    'Amount': amount,
                    'Category': category
                })

        return pd.DataFrame(data)

    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_statement(file_stream, filename):
    """
    Parse financial statement data from various formats
    """
    try:
        if filename.endswith('.pdf'):
            df = parse_pdf(file_stream)
        elif filename.endswith('.csv'):
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