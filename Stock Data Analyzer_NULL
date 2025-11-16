# This script demonstrates how to fetch the financial data
# you need using the 'yfinance' library, as discussed in Option 1.

import yfinance as yf
import pandas as pd

# Set pandas to display all rows/cols for clean printing
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def get_financial_xray(ticker_symbol):
    """
    Fetches financial data for a given stock ticker and calculates
    key ratios from the "Balance Sheet X-Ray" document.
    """
    print(f"--- Fetching Data for {ticker_symbol} ---")
    
    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker_symbol)

        # --- 1. Get the Key Financial Statements ---
        
        # Get Income Statement (Annual)
        # We use .T to transpose the table to make it easier to read
        income_stmt = stock.income_stmt.T
        print(f"\nSuccessfully fetched Income Statement.")

        # Get Balance Sheet (Annual)
        balance_sheet = stock.balance_sheet.T
        print("Successfully fetched Balance Sheet.")

        # Get Cash Flow Statement (Annual)
        cash_flow = stock.cash_flow.T
        print("Successfully fetched Cash Flow Statement.\n")
        
        # --- 2. Calculate Ratios from Your Documents ---
        
        # We'll focus on the most recent full year.
        # .iloc[0] grabs the most recent row (year)
        most_recent_year = income_stmt.index[0]
        print(f"--- Running Analysis for {most_recent_year.year} ---")

        # --- Ratio 1: Cash Conversion Ratio (from Page 6) ---
        # Heuristic: "Compare operating cash flow (CFO) to net income."
        # Ratio = CFO / Net Income. "If this ratio is consistently low <0.8... it's a warning."
        
        try:
            # Get data from Income Statement
            net_income = income_stmt.loc[most_recent_year, 'Net Income']

            # Get data from Cash Flow Statement
            cfo = cash_flow.loc[most_recent_year, 'Operating Cash Flow']

            if net_income and cfo and net_income > 0:
                cash_conversion_ratio = cfo / net_income
                print(f"\n[Cash Flow Analysis]")
                print(f"Net Income: ${net_income:,.0f}")
                print(f"Operating Cash Flow (CFO): ${cfo:,.0f}")
                print(f"Cash Conversion Ratio (CFO / Net Income): {cash_conversion_ratio:.2f}")

                if cash_conversion_ratio < 0.8:
                    print("HEURISTIC WARNING: Cash Conversion Ratio is below 0.8.")
                    print("This may be a red flag (Page 6). Cash flow is not keeping up with reported profits.")
                else:
                    print("HEURISTIC CHECK: Cash flow appears healthy relative to Net Income.")
            
        except KeyError:
            print("\n[Cash Flow Analysis]")
            print("Could not calculate Cash Conversion Ratio. Data missing (e.g., 'Net Income' or 'Operating Cash Flow').")
        except Exception as e:
            print(f"An error occurred during Cash Flow analysis: {e}")


        # --- Ratio 2: Current Ratio (from Page 1) ---
        # Heuristic: "General liquidity gauge."
        # Ratio = Current Assets / Current Liabilities
        
        try:
            # Get data from Balance Sheet
            current_assets = balance_sheet.loc[most_recent_year, 'Current Assets']
            current_liabilities = balance_sheet.loc[most_recent_year, 'Current Liabilities']
            
            if current_assets and current_liabilities and current_liabilities > 0:
                current_ratio = current_assets / current_liabilities
                print(f"\n[Liquidity Analysis]")
                print(f"Current Assets: ${current_assets:,.0f}")
                print(f"Current Liabilities: ${current_liabilities:,.0f}")
                print(f"Current Ratio: {current_ratio:.2f}")

                if current_ratio < 1.0:
                    print("HEURISTIC WARNING: Current Ratio is below 1.0 (Page 1).")
                    print("This suggests a potential liquidity risk.")
                elif current_ratio > 3.0:
                     print("HEURISTIC NOTE: Current Ratio is high (>3.0) (Page 1).")
                     print("This could suggest inefficient use of assets (e.g., inventory sitting idle).")
                else:
                    print("HEURISTIC CHECK: Current Ratio appears to be in a healthy range (1.0 - 3.0).")

        except KeyError:
            print("\n[Liquidity Analysis]")
            print("Could not calculate Current Ratio. Data missing (e.g., 'Current Assets' or 'Current Liabilities').")
        except Exception as e:
            print(f"An error occurred during Liquidity analysis: {e}")

    except Exception as e:
        print(f"\nFailed to fetch data for {ticker_symbol}. Error: {e}")
        print("This could be due to an invalid ticker, or a temporary network/scraping issue.")


# --- Run the Analyzer ---
# You can change 'MSFT' to any ticker (e.g., 'AAPL', 'GOOGL', 'TSLA')
get_financial_xray('MSFT')
