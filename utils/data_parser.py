import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
import re
from datetime import datetime

def parse_pdf(file_stream):
    """
    Extract tabular data from PDF file with enhanced parsing
    """
    try:
        # Create PDF reader object
        pdf = PdfReader(file_stream)

        # Extract text from all pages
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

        # Enhanced data extraction
        data = []
        lines = text.split('\n')

        # Common date formats in financial statements
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',        # YYYY-MM-DD
            r'[A-Za-z]+ \d{1,2},? \d{4}', # Month DD, YYYY
            r'\d{1,2}-[A-Za-z]{3}-\d{4}'  # DD-Mon-YYYY
        ]

        # Amount patterns
        amount_pattern = r'[-+]?\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'

        # Category keywords
        category_patterns = {
            'Equity': ['stock', 'equity', 'share', 'dividend', 'etf'],
            'Fixed Income': ['bond', 'fixed income', 'interest', 'coupon'],
            'Cash': ['cash', 'money market', 'deposit'],
            'Real Estate': ['reit', 'property', 'real estate'],
            'Alternative': ['commodity', 'crypto', 'alternative']
        }

        for i, line in enumerate(lines):
            # Look for date
            date_match = None
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    date_match = match.group(0)
                    break

            # Look for amount
            amount_match = re.search(amount_pattern, line)

            if date_match and amount_match:
                try:
                    # Parse date
                    date_str = date_match
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%d-%b-%Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue

                    # Clean and parse amount
                    amount_str = amount_match.group(0)
                    amount = float(amount_str.replace('$', '').replace(',', '').strip())

                    # Determine category
                    category = 'Other'
                    line_lower = line.lower()
                    for cat, keywords in category_patterns.items():
                        if any(keyword in line_lower for keyword in keywords):
                            category = cat
                            break

                    # Look for transaction type in surrounding lines
                    context = ' '.join(lines[max(0, i-2):min(len(lines), i+3)]).lower()
                    if 'purchase' in context or 'buy' in context:
                        amount = abs(amount)
                    elif 'sale' in context or 'sell' in context:
                        amount = -abs(amount)

                    data.append({
                        'Date': parsed_date.strftime('%Y-%m-%d'),
                        'Amount': amount,
                        'Category': category
                    })

                except Exception as e:
                    print(f"Warning: Skipping line due to parsing error: {e}")
                    continue

        if not data:
            raise ValueError("No valid financial data found in the PDF")

        df = pd.DataFrame(data)
        return df

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
            raise ValueError(f"Missing required columns in the statement. Required: {required_columns}, Found: {list(df.columns)}")

        # Clean and preprocess data
        df['Date'] = pd.to_datetime(df['Date'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

        # Drop rows with invalid data
        df = df.dropna(subset=['Date', 'Amount'])

        if len(df) == 0:
            raise ValueError("No valid data rows found after cleaning")

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
    if row['Category'].lower() in ['equity', 'stock', 'etf']:
        return row['Amount']
    return 0

def calculate_risk_score(row):
    """
    Calculate risk score based on transaction parameters
    """
    risk_weights = {
        'Equity': 1.5,
        'Fixed Income': 0.8,
        'Cash': 0.2,
        'Real Estate': 1.2,
        'Alternative': 1.8,
        'Other': 1.0
    }

    base_score = 1.0
    weight = risk_weights.get(row['Category'], 1.0)
    return base_score * weight * (abs(row['Amount']) / 10000)  # Scale by transaction size