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

# --- Helper function to safely get data ---
def safe_get(df, *keys):
    """
    Safely get a value from a DataFrame row (Series) by trying multiple keys.
    Returns None if all keys fail.
    """
    for key in keys:
        try:
            val = df[key]
            return val
        except KeyError:
            continue
    return None

# --- Header ---
st.title("Financial X-Ray Tool 📈")
st.markdown("Enter a public company ticker (from Yahoo Finance) to automatically run a financial X-Ray based on your analysis documents.")

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

                # 2. Get Financial Statements (Annual)
                try:
                    income_stmt_t = stock.income_stmt.T
                    balance_sheet_t = stock.balance_sheet.T
                    cash_flow_t = stock.cash_flow.T
                except Exception as e:
                    st.error(f"Could not retrieve financial statements for {ticker_symbol.upper()}.")
                    st.error(f"This ticker might be for an ETF, index, or cryptocurrency. Error details: {e}")
                    st.stop() # Stop the script

                # Check if data is empty
                if income_stmt_t.empty or balance_sheet_t.empty or cash_flow_t.empty:
                    st.error(f"No financial data found for {ticker_symbol.upper()}. Please check the ticker.")
                    st.stop() # Stop the script
                
                # Get most recent and previous year data
                try:
                    current_year = income_stmt_t.iloc[0]
                    prev_year = income_stmt_t.iloc[1]
                    current_year_bs = balance_sheet_t.iloc[0]
                    prev_year_bs = balance_sheet_t.iloc[1]
                    current_year_cf = cash_flow_t.iloc[0]
                except IndexError:
                    st.error("Not enough historical data for trend analysis (need at least 2 years).")
                    st.stop()

                st.header(f"Analysis for {ticker_symbol.upper()} ({current_year.name.year})", divider="rainbow")

                # --- 3. Run Analysis & Display Results ---

                # --- Analysis 1: Cash Conversion Ratio (Balance Sheet Doc, Pg 6 / Income Stmt Doc, Pg 3) ---
                st.subheader("1. Cash Conversion Ratio (Earnings Quality)")
                try:
                    net_income = safe_get(current_year, 'Net Income')
                    cfo = safe_get(current_year_cf, 'Operating Cash Flow', 'Total Cash From Operating Activities')

                    if net_income and cfo and net_income > 0:
                        ratio = cfo / net_income
                        st.metric(label="Cash Conversion Ratio (CFO / Net Income)", value=f"{ratio:.2f}")

                        st.write(f"**Net Income:** ${net_income:,.0f}")
                        st.write(f"**Operating Cash Flow:** ${cfo:,.0f}")

                        if ratio < 0.8:
                            st.error("🔴 HEURISTIC WARNING (Doc 1, Pg 6 / Doc 2, Pg 3): Ratio is below 0.8. This is a red flag. Cash flow is not keeping up with reported profits.")
                        else:
                            st.success("✅ HEURISTIC CHECK: Ratio is healthy. Cash flows are keeping pace with Net Income.")
                    else:
                        st.warning("Could not calculate: Net Income was zero, negative, or data was missing.")

                except Exception as e:
                    st.error(f"An error occurred during Cash Conversion analysis: {e}")

                # --- Analysis 2: Current Ratio (Balance Sheet Doc, Pg 1) ---
                st.subheader("2. Current Ratio (Liquidity)")
                try:
                    current_assets = safe_get(current_year_bs, 'Current Assets', 'Total Current Assets')
                    current_liabilities = safe_get(current_year_bs, 'Current Liabilities', 'Total Current Liabilities')

                    if current_assets and current_liabilities and current_liabilities > 0:
                        ratio = current_assets / current_liabilities
                        st.metric(label="Current Ratio (Assets / Liabilities)", value=f"{ratio:.2f}")

                        st.write(f"**Current Assets:** ${current_assets:,.0f}")
                        st.write(f"**Current Liabilities:** ${current_liabilities:,.0f}")

                        if ratio < 1.0:
                            st.error("🔴 HEURISTIC WARNING (Doc 1, Pg 1): Ratio is below 1.0. This is a 'clear red flag' suggesting potential liquidity risk.")
                        elif ratio > 3.0:
                            st.warning("🟡 HEURISTIC NOTE (Doc 1, Pg 1): Ratio is high (>3.0). This might indicate inefficient use of assets (e.g., inventory sitting idle).")
                        else:
                            st.success("✅ HEURISTIC CHECK: Ratio is in the healthy 1.0 - 3.0 range.")
                    else:
                        st.warning("Could not calculate: Current Liabilities were zero or data was missing.")
                
                except Exception as e:
                    st.error(f"An error occurred during Liquidity analysis: {e}")
                
                # --- Analysis 3: Revenue Quality (Income Stmt Doc, Pg 1) ---
                st.subheader("3. Revenue Quality (Receivables)")
                try:
                    revenue_cy = safe_get(current_year, 'Total Revenue', 'Revenue')
                    revenue_py = safe_get(prev_year, 'Total Revenue', 'Revenue')
                    receivables_cy = safe_get(current_year_bs, 'Accounts Receivable', 'Receivables', 'Net Receivables')
                    receivables_py = safe_get(prev_year_bs, 'Accounts Receivable', 'Receivables', 'Net Receivables')

                    if all([revenue_cy, revenue_py, receivables_cy, receivables_py, revenue_py > 0, receivables_py > 0]):
                        revenue_growth = (revenue_cy - revenue_py) / revenue_py
                        receivables_growth = (receivables_cy - receivables_py) / receivables_py

                        st.metric(label="Revenue Growth", value=f"{revenue_growth:,.1%}")
                        st.metric(label="Receivables Growth", value=f"{receivables_growth:,.1%}")

                        if receivables_growth > revenue_growth:
                            st.error("🔴 HEURISTIC WARNING (Doc 2, Pg 1): Receivables are growing faster than revenue. This is a red flag for 'channel stuffing' or aggressive revenue recognition.")
                        else:
                            st.success("✅ HEURISTIC CHECK: Revenue is growing faster than receivables. This is a healthy sign.")
                    else:
                        st.warning("Could not calculate: Missing data for Revenue or Receivables for trend analysis.")

                except Exception as e:
                    st.error(f"An error occurred during Revenue Quality analysis: {e}")

                # --- Analysis 4: Gross Margin (Income Stmt Doc, Pg 1) ---
                st.subheader("4. Gross Margin Analysis")
                try:
                    revenue_cy = safe_get(current_year, 'Total Revenue', 'Revenue')
                    gross_profit_cy = safe_get(current_year, 'Gross Profit')
                    gross_profit_py = safe_get(prev_year, 'Gross Profit')
                    
                    if revenue_cy and gross_profit_cy and revenue_cy > 0:
                        gross_margin_cy = gross_profit_cy / revenue_cy
                        st.metric(label=f"Gross Margin ({current_year.name.year})", value=f"{gross_margin_cy:.1%}")

                        # Check trend
                        if revenue_py and gross_profit_py and revenue_py > 0:
                            gross_margin_py = gross_profit_py / revenue_py
                            st.write(f"**Previous Year Margin:** {gross_margin_py:.1%}")
                            if gross_margin_cy > gross_margin_py:
                                st.success("✅ HEURISTIC CHECK (Doc 2, Pg 1): Gross Margin is rising. This indicates pricing power or a competitive advantage.")
                            else:
                                st.warning("🟡 HEURISTIC NOTE (Doc 2, Pg 1): Gross Margin is stable or falling. Monitor this trend.")
                    else:
                        st.warning("Could not calculate: Missing data for Gross Profit or Revenue.")
                
                except Exception as e:
                    st.error(f"An error occurred during Gross Margin analysis: {e}")

                # --- Analysis 5: Operating Expenses (Income Stmt Doc, Pg 2) ---
                st.subheader("5. Operating Expense Analysis")
                try:
                    revenue_cy = safe_get(current_year, 'Total Revenue', 'Revenue')
                    sga_cy = safe_get(current_year, 'Selling General Administrative')
                    rd_cy = safe_get(current_year, 'Research Development')

                    if revenue_cy and revenue_cy > 0:
                        if sga_cy:
                            sga_ratio = sga_cy / revenue_cy
                            st.metric(label="SG&A as % of Revenue", value=f"{sga_ratio:.1%}")
                            if sga_ratio > 0.5:
                                st.warning("🟡 HEURISTIC NOTE (Doc 2, Pg 2): SG&A is >50% of revenue. This is high, typical for some high-growth SaaS, but could signal inefficiency.")
                        
                        if rd_cy:
                            rd_ratio = rd_cy / revenue_cy
                            st.metric(label="R&D as % of Revenue", value=f"{rd_ratio:.1%}")
                        
                        # Operating Leverage
                        sga_py = safe_get(prev_year, 'Selling General Administrative')
                        revenue_py = safe_get(prev_year, 'Total Revenue', 'Revenue')
                        if all([sga_cy, sga_py, revenue_cy, revenue_py, sga_py > 0, revenue_py > 0]):
                            revenue_growth = (revenue_cy - revenue_py) / revenue_py
                            sga_growth = (sga_cy - sga_py) / sga_py
                            
                            st.write(f"**Revenue Growth:** {revenue_growth:.1%}")
                            st.write(f"**SG&A Growth:** {sga_growth:.1%}")
                            if revenue_growth > sga_growth:
                                st.success("✅ HEURISTIC CHECK (Doc 2, Pg 2): Revenue is growing faster than SG&A. This shows positive operating leverage.")
                            else:
                                st.warning("🟡 HEURISTIC NOTE (Doc 2, Pg 2): SG&A is growing faster than revenue. This indicates 'cost creep' and negative leverage.")
                    else:
                         st.warning("Could not calculate: Missing data for Operating Expenses or Revenue.")

                except Exception as e:
                    st.error(f"An error occurred during Operating Expense analysis: {e}")

                # --- Analysis 6: Profitability & Debt (Income Stmt Doc, Pg 3) ---
                st.subheader("6. Profitability & Debt Coverage")
                try:
                    ebit = safe_get(current_year, 'EBIT', 'Operating Income')
                    revenue_cy = safe_get(current_year, 'Total Revenue', 'Revenue')
                    interest_expense = safe_get(current_year, 'Interest Expense')

                    if ebit and revenue_cy and revenue_cy > 0:
                        ebit_margin = ebit / revenue_cy
                        st.metric(label="EBIT Margin", value=f"{ebit_margin:.1%}")
                    
                    if ebit and interest_expense and interest_expense > 0:
                        # Make interest expense positive for ratio calculation
                        interest_expense_val = abs(interest_expense) 
                        coverage_ratio = ebit / interest_expense_val
                        st.metric(label="Interest Coverage Ratio (EBIT / Interest)", value=f"{coverage_ratio:.1f}x")

                        if coverage_ratio < 2.0:
                            st.error("🔴 HEURISTIC WARNING (Doc 2, Pg 3): Interest Coverage is below 2x. This is a major warning sign for financial distress.")
                        else:
                            st.success("✅ HEURISTIC CHECK: Interest Coverage is healthy.")
                    
                    if not (ebit and revenue_cy and interest_expense):
                        st.warning("Could not calculate: Missing data for EBIT, Revenue, or Interest Expense.")

                except Exception as e:
                    st.error(f"An error occurred during Profitability analysis: {e}")

                # --- Analysis 7: Accrual Ratio (Income Stmt Doc, Pg 4) ---
                st.subheader("7. Accrual Ratio (Earnings Quality)")
                try:
                    net_income = safe_get(current_year, 'Net Income')
                    cfo = safe_get(current_year_cf, 'Operating Cash Flow', 'Total Cash From Operating Activities')
                    total_assets = safe_get(current_year_bs, 'Total Assets')

                    if all([net_income, cfo, total_assets, total_assets > 0]):
                        accrual_ratio = (net_income - cfo) / total_assets
                        st.metric(label="Accrual Ratio ((NI - CFO) / Total Assets)", value=f"{accrual_ratio:.2%}")

                        if accrual_ratio > 0.05: # Using 5% as a "high positive" heuristic
                            st.error("🔴 HEURISTIC WARNING (Doc 2, Pg 4): Accrual Ratio is high and positive. This is a red flag for 'paper profits' and poor earnings quality.")
                        else:
                            st.success("✅ HEURISTIC CHECK: Accrual Ratio is low or negative, suggesting earnings are backed by cash.")
                    else:
                        st.warning("Could not calculate: Missing data for Net Income, CFO, or Total Assets.")

                except Exception as e:
                    st.error(f"An error occurred during Accrual Ratio analysis: {e}")

            except Exception as e:
                st.error(f"Failed to process ticker {ticker_symbol.upper()}. Is it a valid symbol?")
                st.error(f"Error details: {e}")

# --- Footer ---
st.markdown("---")
st.caption("This tool is for educational purposes only, based on financial heuristics from your documents. Data is sourced from Yahoo Finance and is not financial advice.")
