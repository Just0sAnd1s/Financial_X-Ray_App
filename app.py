# This is your complete web application.
# To run it:
# 1. Install libraries: pip install -r requirements.txt
# 2. Run in terminal: streamlit run app.py

import streamlit as st
import yfinance as yf
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial X-Ray Tool",
    page_icon="📈",
    layout="centered"
)

# --- Header ---
st.title("Financial X-Ray Tool 📈")
st.markdown("Enter a public company ticker (from Yahoo Finance) to automatically run the '15-Minute X-Ray' analysis based on your documents.")

# --- Ticker Input ---
ticker_symbol = st.text_input("Enter Ticker Symbol (e.g., AAPL, MSFT, TSLA)", "AAPL")

# --- Analysis Button ---
if st.button("Run X-Ray Analysis"):
    if not ticker_symbol:
        st.warning("Please enter a ticker symbol to analyze.")
    else:
        with st.spinner(f"Fetching data for {ticker_symbol.upper()}..."):
            try:
                # 1. Fetch Data
                stock = yf.Ticker(ticker_symbol)

                # 2. Get Financial Statements
                try:
                    income_stmt = stock.income_stmt.T
                    balance_sheet = stock.balance_sheet.T
                    cash_flow = stock.cash_flow.T
                except Exception as e:
                    st.error(f"Could not retrieve financial statements for {ticker_symbol.upper()}.")
                    st.error(f"This ticker might be for an ETF, index, or cryptocurrency, not a company. Error details: {e}")
                    st.stop() # Stop the script

                # Check if data is empty
                if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
                    st.error(f"No financial data found for {ticker_symbol.upper()}. Please check the ticker.")
                    st.stop() # Stop the script

                # Get the most recent full year for analysis
                most_recent_year = income_stmt.index[0]
                st.header(f"Analysis for {ticker_symbol.upper()} ({most_recent_year.year})", divider="rainbow")

                # --- 3. Run Analysis & Display Results ---

                # --- Analysis 1: Cash Conversion Ratio (from Page 6) ---
                st.subheader("1. Cash Conversion Ratio")
                try:
                    net_income = income_stmt.loc[most_recent_year, 'Net Income']
                    cfo = cash_flow.loc[most_recent_year, 'Operating Cash Flow']

                    if net_income and cfo and net_income > 0:
                        ratio = cfo / net_income
                        st.metric(label="Cash Conversion Ratio (CFO / Net Income)", value=f"{ratio:.2f}")

                        st.write(f"**Net Income:** ${net_income:,.0f}")
                        st.write(f"**Operating Cash Flow:** ${cfo:,.0f}")

                        if ratio < 0.8:
                            st.error("🔴 HEURISTIC WARNING (Page 6): Ratio is below 0.8. This is a red flag. Cash flow is not keeping up with reported profits.")
                        else:
                            st.success("✅ HEURISTIC CHECK: Ratio is healthy. Cash flows are keeping pace with Net Income.")
                    else:
                        st.warning("Could not calculate: Net Income was zero, negative, or data was missing.")

                except KeyError:
                    st.warning("Could not calculate: 'Net Income' or 'Operating Cash Flow' data not found in the statement.")
                except Exception as e:
                    st.error(f"An error occurred during Cash Conversion analysis: {e}")

                # --- Analysis 2: Current Ratio (from Page 1) ---
                st.subheader("2. Current Ratio (Liquidity)")
                try:
                    current_assets = balance_sheet.loc[most_recent_year, 'Current Assets']
                    current_liabilities = balance_sheet.loc[most_recent_year, 'Current Liabilities']

                    if current_assets and current_liabilities and current_liabilities > 0:
                        ratio = current_assets / current_liabilities
                        st.metric(label="Current Ratio (Assets / Liabilities)", value=f"{ratio:.2f}")

                        st.write(f"**Current Assets:** ${current_assets:,.0f}")
                        st.write(f"**Current Liabilities:** ${current_liabilities:,.0f}")

                        if ratio < 1.0:
                            st.error("🔴 HEURISTIC WARNING (Page 1): Ratio is below 1.0. This is a 'clear red flag' suggesting potential liquidity risk.")
                        elif ratio > 3.0:
                            st.warning("🟡 HEURISTIC NOTE (Page 1): Ratio is high (>3.0). This might indicate inefficient use of assets (e.g., inventory sitting idle).")
                        else:
                            st.success("✅ HEURISTIC CHECK: Ratio is in the healthy 1.0 - 3.0 range.")
                    else:
                        st.warning("Could not calculate: Current Liabilities were zero or data was missing.")
                
                except KeyError:
                    st.warning("Could not calculate: 'Current Assets' or 'Current Liabilities' data not found.")
                except Exception as e:
                    st.error(f"An error occurred during Liquidity analysis: {e}")

            except Exception as e:
                st.error(f"Failed to process ticker {ticker_symbol.upper()}. Is it a valid symbol?")
                st.error(f"Error details: {e}")

# --- Footer ---
st.markdown("---")
st.caption("This tool is for educational purposes only, based on the '15-Minute X-Ray' heuristics. Data is sourced from Yahoo Finance and is not financial advice.")
