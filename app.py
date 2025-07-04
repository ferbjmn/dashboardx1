import yfinance as yf
import time
import pandas as pd
import streamlit as st

# Lista de tickers de las compañías a analizar (ejemplo)
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Inicializar un dataframe vacío para almacenar los datos recopilados
data = []

# Sección 1: Recopilación de datos financieros de las compañías
def get_financial_data(ticker):
    company = yf.Ticker(ticker)
    info = company.info
    balance_sheet = company.balance_sheet
    cashflow = company.cashflow
    financials = company.financials

    # Extraemos los datos relevantes
    company_data = {
        'Ticker': ticker,
        'Company': info.get('longName', 'N/A'),
        'Sector': info.get('sector', 'N/A'),
        'Industry': info.get('industry', 'N/A'),
        'Country': info.get('country', 'N/A'),
        'P/E': info.get('trailingPE', 'N/A'),
        'P/BV': info.get('priceToBook', 'N/A'),
        'P/FCF': info.get('priceToFreeCashflow', 'N/A'),
        'Dividend': info.get('dividendRate', 'N/A'),
        'Payout Ratio': info.get('payoutRatio', 'N/A'),
        'ROE': financials.loc['Net Income'] / balance_sheet.loc['Total Equity'] if 'Net Income' in financials.index and 'Total Equity' in balance_sheet.index else 'N/A',
        'ROA': financials.loc['Net Income'] / balance_sheet.loc['Total Assets'] if 'Net Income' in financials.index and 'Total Assets' in balance_sheet.index else 'N/A',
        'Current Ratio': balance_sheet.loc['Total Current Assets'] / balance_sheet.loc['Total Current Liabilities'] if 'Total Current Assets' in balance_sheet.index and 'Total Current Liabilities' in balance_sheet.index else 'N/A',
        'Operating Cash Flow': cashflow.loc['Operating Cash Flow'][-1] if 'Operating Cash Flow' in cashflow.index else 'N/A',
        'Leverage Ratio': balance_sheet.loc['Long Term Debt'] / financials.loc['EBITDA'] if 'EBITDA' in financials.index else 'N/A',
        'Long Term Debt / Capital': balance_sheet.loc['Long Term Debt'] / balance_sheet.loc['Total Equity'] if 'Long Term Debt' in balance_sheet.index and 'Total Equity' in balance_sheet.index else 'N/A',
        'Debt / Capital': balance_sheet.loc['Total Liabilities'] / balance_sheet.loc['Total Equity'] if 'Total Liabilities' in balance_sheet.index and 'Total Equity' in balance_sheet.index else 'N/A',
        'Operating Margin': financials.loc['Operating Income'] / financials.loc['Total Revenue'] if 'Operating Income' in financials.index and 'Total Revenue' in financials.index else 'N/A',
        'Profit Margin': financials.loc['Net Income'] / financials.loc['Total Revenue'] if 'Net Income' in financials.index and 'Total Revenue' in financials.index else 'N/A',
        'EBIT': financials.loc['EBIT'][-1] if 'EBIT' in financials.index else 'N/A',
        'Free Cash Flow': cashflow.loc['Free Cash Flow'][-1] if 'Free Cash Flow' in cashflow.index else 'N/A',
        'CAPEX': cashflow.loc['Capital Expenditures'][-1] if 'Capital Expenditures' in cashflow.index else 'N/A',
        'Market Capitalization': info.get('marketCap', 'N/A'),
        'Shares Outstanding': info.get('sharesOutstanding', 'N/A'),
        'Cash': balance_sheet.loc['Cash'][-1] if 'Cash' in balance_sheet.index else 'N/A',
        'Total Liabilities': balance_sheet.loc['Total Liabilities'][-1] if 'Total Liabilities' in balance_sheet.index else 'N/A',
        'Equity': balance_sheet.loc['Total Equity'][-1] if 'Total Equity' in balance_sheet.index else 'N/A',
    }

    return company_data

# Recopilar datos para todas las compañías
for ticker in tickers:
    company_data = get_financial_data(ticker)
    data.append(company_data)
    time.sleep(0.5)  # Pausar para evitar bloqueo por parte de yfinance

# Convertir los datos a un DataFrame
df = pd.DataFrame(data)

# Mostrar el dataframe con los datos recopilados en Streamlit
st.write("### Financial Data", df)

# Sección 2: Visualización de los Ratios Financieros
df_ratios = df[['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'P/E', 'P/BV', 'P/FCF', 'Dividend', 'Payout Ratio',
                'ROE', 'ROA', 'Current Ratio', 'Long Term Debt / Capital', 'Debt / Capital', 'Operating Margin', 
                'Profit Margin', 'Market Capitalization', 'Shares Outstanding', 'Free Cash Flow', 'CAPEX']]

st.write("### Financial Ratios", df_ratios)

# Sección 3: Cálculo de WACC, ROIC y la Conclusión sobre la Creación de Valor
def calculate_wacc_roic_and_conclusion(ticker, balance_sheet, financials, cashflow, info):
    # Obtener los valores de la compañía
    equity = balance_sheet.loc['Total Equity'][-1] if 'Total Equity' in balance_sheet.index else 0
    total_debt = balance_sheet.loc['Total Liabilities'][-1] if 'Total Liabilities' in balance_sheet.index else 0
    cash = balance_sheet.loc['Cash'][-1] if 'Cash' in balance_sheet.index else 0
    ebit = financials.loc['EBIT'][-1] if 'EBIT' in financials.index else 0
    market_cap = info.get('marketCap', 0)
    
    # Evitar la división por cero
    total_value = equity + total_debt
    if total_value == 0:
        return None, None, "Total value is zero, cannot calculate WACC and ROIC"
    
    # Estimación externa de la Tasa Libre de Riesgo y Beta
    risk_free_rate = 0.03  # Tasa libre de riesgo (ejemplo: 3%)
    market_return = 0.08  # Rendimiento esperado del mercado (ejemplo: 8%)
    beta = info.get('beta', 1)  # Beta de la empresa, disponible en yfinance
    
    # Estimación de la tasa de interés de la deuda (Cost of Debt)
    cost_of_debt = 0.05  # Estimación del costo de la deuda (5%)
    
    # Estimación de la Tasa Impositiva
    tax_rate = 0.21  # Estimación de la tasa impositiva (21%)
    
    # Cálculo de Cost of Equity (CAPM)
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    
    # Cálculo de WACC
    wacc = (equity / total_value * cost_of_equity) + (total_debt / total_value * cost_of_debt * (1 - tax_rate))
    
    # Cálculo de ROIC
    nopat = ebit * (1 - tax_rate) if ebit > 0 else 0
    invested_capital = equity + total_debt - cash
    roic = nopat / invested_capital if invested_capital > 0 else 0
    
    # Conclusión: Crear valor o destruir valor
    if roic > wacc:
        conclusion = "La compañía está creando valor."
    elif roic < wacc:
        conclusion = "La compañía está destruyendo valor."
    else:
        conclusion = "La compañía está en el umbral de crear o destruir valor."

    return wacc, roic, conclusion

# Aplicar el cálculo de WACC, ROIC y la conclusión sobre la creación de valor para todas las compañías
wacc_roic_conclusion_data = []

for ticker in tickers:
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    financials = company.financials
    cashflow = company.cashflow
    info = company.info
    
    # Calcular WACC, ROIC y la conclusión sobre creación de valor
    wacc, roic, conclusion = calculate_wacc_roic_and_conclusion(ticker, balance_sheet, financials, cashflow, info)
    
    # Almacenar los resultados en un diccionario
    wacc_roic_conclusion_data.append({
        'Ticker': ticker,
        'WACC': wacc,
        'ROIC': roic,
        'Conclusion': conclusion
    })
    
    time.sleep(0.5)  # Pausar para evitar bloqueos por parte de yfinance

# Convertir los resultados a un DataFrame
wacc_roic_conclusion_df = pd.DataFrame(wacc_roic_conclusion_data)

# Mostrar el dataframe con los resultados de WACC, ROIC y la conclusión sobre la creación de valor
st.write("### Resultados de WACC, ROIC y Creación de Valor", wacc_roic_conclusion_df)

# Sección 4: Análisis de Solvencia de Deuda
def calculate_debt_solvency_ratios(ticker, balance_sheet, financials, cashflow, info):
    # Obtener los valores de la compañía
    current_assets = balance_sheet.loc['Total Current Assets'][-1] if 'Total Current Assets' in balance_sheet.index else 0
    current_liabilities = balance_sheet.loc['Total Current Liabilities'][-1] if 'Total Current Liabilities' in balance_sheet.index else 0
    inventories = balance_sheet.loc['Inventory'][-1] if 'Inventory' in balance_sheet.index else 0
    total_debt = balance_sheet.loc['Total Liabilities'][-1] if 'Total Liabilities' in balance_sheet.index else 0
    total_assets = balance_sheet.loc['Total Assets'][-1] if 'Total Assets' in balance_sheet.index else 0
    equity = balance_sheet.loc['Total Equity'][-1] if 'Total Equity' in balance_sheet.index else 0
    ebit = financials.loc['EBIT'][-1] if 'EBIT' in financials.index else 0
    interest_expense = financials.loc['Interest Expense'][-1] if 'Interest Expense' in financials.index else 0

    # Calcular los ratios
    current_ratio = current_assets / current_liabilities if current_liabilities != 0 else 'N/A'
    quick_ratio = (current_assets - inventories) / current_liabilities if current_liabilities != 0 else 'N/A'
    debt_to_equity = total_debt / equity if equity != 0 else 'N/A'
    debt_to_assets = total_debt / total_assets if total_assets != 0 else 'N/A'
    interest_coverage_ratio = ebit / interest_expense if interest_expense != 0 else 'N/A'
    total_debt_to_total_capital = total_debt / (total_debt + equity) if (total_debt + equity) != 0 else 'N/A'

    # Devolver los ratios calculados
    return {
        'Ticker': ticker,
        'Current Ratio': current_ratio,
        'Quick Ratio': quick_ratio,
        'Debt-to-Equity Ratio': debt_to_equity,
        'Debt-to-Assets Ratio': debt_to_assets,
        'Interest Coverage Ratio': interest_coverage_ratio,
        'Total Debt to Total Capital': total_debt_to_total_capital
    }

# Aplicar el cálculo de solvencia de deuda para todas las compañías
debt_solveny_data = []

for ticker in tickers:
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    financials = company.financials
    cashflow = company.cashflow
    info = company.info
    
    # Calcular los ratios de solvencia de deuda
    debt_ratios = calculate_debt_solvency_ratios(ticker, balance_sheet, financials, cashflow, info)
    
    # Almacenar los resultados en un diccionario
    debt_solveny_data.append(debt_ratios)
    
    time.sleep(0.5)  # Pausar para evitar bloqueos por parte de yfinance

# Convertir los resultados a un DataFrame
debt_solveny_df = pd.DataFrame(debt_solveny_data)

# Mostrar el dataframe con los resultados de solvencia de deuda
st.write("### Ratios de Solvencia de Deuda", debt_solveny_df)
