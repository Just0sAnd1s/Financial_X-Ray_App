# Financial_X-Ray_App

# Financial X-Ray Tool 📈

This is a simple web application built in Python using Streamlit that performs a "FIR X-Ray" financial analysis on public companies.

It automatically fetches financial data (Balance Sheet, Income Statement, Cash Flow) from Yahoo Finance (yfinance) and calculates key ratios to identify potential strengths or "red flags" based on common financial heuristics.

### Features

Automatic Data Fetching: Just enter a company's stock ticker (e.g., ```AAPL```, ```MSFT```) to get the latest annual data.

Cash Conversion Ratio: Analyzes the quality of earnings by comparing Operating Cash Flow to Net Income.

Current Ratio (Liquidity): Assesses short-term financial health and liquidity risk.

## How to Run Locally

### 1. Clone the Repository:

```
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
```

### 2. Install Dependencies:
Make sure you have Python installed. Then, install the required libraries from the [requirements.txt](requirements.txt) file:

```
pip install -r requirements.txt
```

### 3. Run the App:
Use the Streamlit command to run the [app.py](app.py) file:

```
streamlit run app.py
```

Your default web browser will automatically open with the running application.

## How to Deploy for Free (Streamlit Cloud)

You can host this application for free on Streamlit Community Cloud.

### 1. Upload to GitHub:
Push your project (including [app.py](app.py), [requirements.txt](requirements.txt), and this [README.md](README.md) to a new public repository on your GitHub account.

### 2. Sign Up for Streamlit Cloud:
Go to Streamlit Community Cloud and sign up for a free account.

### 3. Deploy the App:
  - From your Streamlit dashboard, click "New app".
  - Connect your GitHub account.
  - Select your repository, the correct branch (usually main), and the [app.py](app.py) file.
  - Click "Deploy!"

Your app will be built and deployed, and you'll get a free, shareable URL (e.g., your-app-name.streamlit.app).

> [!NOTE]
> **Disclaimer**
> 
> This tool is for educational and informational purposes only. The analysis provided is based on simplified heuristics and is not financial advice. All data is sourced from Yahoo Finance and may be subject to errors or delays.


