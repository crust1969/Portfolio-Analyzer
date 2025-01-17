import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Funktion zur Überwachung der Portfolio-Performance und KPIs
def check_portfolio_performance(portfolio, stop_loss_limits, start_date, end_date):
    tickers = list(portfolio.keys())
    investments = list(portfolio.values())

    # Historische Daten abrufen
    try:
        data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    except Exception as e:
        st.error(f"Fehler beim Abrufen der historischen Daten: {e}")
        return None, None, []

    # Überprüfung der Daten
    if data.empty:
        st.error("Keine historischen Daten verfügbar.")
        return None, None, []

    # Normalisieren der Daten (alle Kurse starten bei 1)
    data_norm = data.div(data.iloc[0])

    # Berechnung des Portfoliowerts
    portfolio_value = (data_norm * investments).sum(axis=1)

    # Aktuelle Daten abrufen
    try:
        current_data = yf.download(tickers, period='1d')['Adj Close']
    except Exception as e:
        st.error(f"Fehler beim Abrufen der aktuellen Daten: {e}")
        return None, None, []

    if current_data.empty:
        st.error("Keine aktuellen Daten verfügbar.")
        return None, None, []

    current_prices = current_data.iloc[-1]

    # Überprüfung der Stopp-Loss-Grenzen
    previous_prices = data.iloc[-1]
    stop_loss_alerts = []
    for ticker in tickers:
        current_price = current_prices[ticker]
        previous_price = previous_prices[ticker]
        if (previous_price - current_price) / previous_price * 100 >= stop_loss_limits[ticker]:
            stop_loss_alerts.append(f"Stopp-Loss erreicht für {ticker}: aktueller Preis = {current_price:.2f}, Vortagespreis = {previous_price:.2f}, Verlust = {((previous_price - current_price) / previous_price * 100):.2f}%")
    
    return portfolio_value, current_prices, stop_loss_alerts

# Streamlit App
st.title("Portfolio Performance Monitor")
st.write("Überwachung der täglichen Performance und Stopp-Loss-Grenzen Ihres Portfolios")

# Eingabefelder für das Portfolio
st.sidebar.header("Portfolio-Einstellungen")

portfolio = {}
stop_loss_limits = {}

# Standardwerte für das Portfolio
default_portfolio = {
    'ALV.DE': 2250,
    'SAP.DE': 2250,
    'AMZN': 3000,
    'AAPL': 3000,
    'NVDA': 2250,
    'MSFT': 2250
}
default_stop_loss = 10

# Datumseingaben
start_date = st.sidebar.date_input("Startdatum", datetime.today() - pd.DateOffset(years=1))
end_date = st.sidebar.date_input("Enddatum", datetime.today())

# Portfolio-Eingaben
num_stocks = st.sidebar.number_input("Anzahl der Aktien im Portfolio", min_value=1, max_value=20, value=len(default_portfolio))
for i in range(num_stocks):
    ticker = st.sidebar.text_input(f"Ticker-Symbol {i+1}", list(default_portfolio.keys())[i] if i < len(default_portfolio) else "")
    amount = st.sidebar.number_input(f"Investierter Betrag {i+1}", value=list(default_portfolio.values())[i] if i < len(default_portfolio) else 0)
    stop_loss = st.sidebar.number_input(f"Stopp-Loss-Grenze % {i+1}", value=default_stop_loss)
    if ticker:
        portfolio[ticker] = amount
        stop_loss_limits[ticker] = stop_loss

# Schaltfläche zum Überprüfen der Performance
if st.sidebar.button("Portfolio überprüfen"):
    performance, current_prices, stop_loss_alerts = check_portfolio_performance(portfolio, stop_loss_limits, start_date, end_date)

    if performance is not None and current_prices is not None:
        # Plot der Portfolio-Performance
        st.subheader("Portfolio Performance")
        st.line_chart(performance)

        # Anzeige der aktuellen Preise
        st.subheader("Aktuelle Preise")
        st.write(current_prices)

        # Anzeige der Stopp-Loss-Warnungen
        st.subheader("Stopp-Loss-Warnungen")
        if stop_loss_alerts:
            for alert in stop_loss_alerts:
                st.warning(alert)
        else:
            st.success("Keine Stopp-Loss-Grenzen erreicht.")

        # Erstellen und Anzeigen des Plots
        st.subheader("Portfolio Verteilung")
        labels = list(portfolio.keys())
        sizes = list(portfolio.values())
        colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightgreen', 'pink']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
