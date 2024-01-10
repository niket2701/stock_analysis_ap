from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import datetime

app = Flask(__name__)


class StockAnalyzer:
    def __init__(self, ticker_list):
        self.ticker_list = ticker_list
        self.stock_data = self.download_stock_data()
        self.historical_prices = self.get_historical_prices()

    def download_stock_data(self):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        stock = yf.download(self.ticker_list, start='2020-01-01', end=today)
        return stock

    def get_historical_prices(self):
        historical_prices = {}
        for ticker in self.stock_data.columns.get_level_values(1).unique():
            try:
                historical_prices[ticker] = self.stock_data['Close', ticker]
            except KeyError:
                print(f"Close price not found for {ticker}")
        return pd.DataFrame(historical_prices)

    def get_positive_return_stocks(self, cur_date):
        thirty_days_ago = (datetime.datetime.strptime(cur_date, '%Y-%m-%d') - datetime.timedelta(days=30)).strftime(
            '%Y-%m-%d')
        thirty_day_prices = self.historical_prices.loc[thirty_days_ago:cur_date]

        positive_return_stocks = []
        for ticker in thirty_day_prices.columns:
            prices = thirty_day_prices[ticker]
            if len(prices.dropna()) >= 2:  # At least 2 prices are needed to calculate returns
                returns = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100  # Calculating returns as percentage
                if returns > 0:
                    positive_return_stocks.append((ticker, round(returns, 2)))

        return positive_return_stocks


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    input_date = request.form['date']
    nifty_50_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "HINDUNILVR.NS", "INFY.NS",
                        "KOTAKBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BAJFINANCE.NS",
    "BHARTIARTL.NS", "MARUTI.NS", "LT.NS", "WIPRO.NS", "AXISBANK.NS",
    "TECHM.NS", "NESTLEIND.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS",
    "SUNPHARMA.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "IOC.NS", "JSWSTEEL.NS",
    "DRREDDY.NS", "INDUSINDBK.NS", "COALINDIA.NS", "BAJAJ-AUTO.NS", "TITAN.NS",
    "M&M.NS", "UPL.NS", "GRASIM.NS", "HEROMOTOCO.NS", "SHREECEM.NS", "ASIANPAINT.NS",
    "SBILIFE.NS", "BRITANNIA.NS", "DIVISLAB.NS", "CIPLA.NS", "ADANIPORTS.NS",
    "BAJAJFINSV.NS", "HCLTECH.NS", "CIPLA.NS", "TATACONSUM.NS", "DIVISLAB.NS",
    "IOC.NS", "COALINDIA.NS", "JSWSTEEL.NS", "TATAMOTORS.NS", "NESTLEIND.NS"]  # Add your Nifty 50 symbols
    stock_analyzer = StockAnalyzer(nifty_50_symbols)
    positive_return_stocks = stock_analyzer.get_positive_return_stocks(input_date)

    return render_template('result.html', stocks=positive_return_stocks, input_date=input_date)


if __name__ == '__main__':
    app.run(debug=True)
