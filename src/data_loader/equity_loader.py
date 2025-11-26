import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

class EquityLoader:
    """
    A class to fetch equity data from Yahoo Finance.

    This class provides methods to search for companies by name and retrieve their historical stock data.
    """

    def __init__(self):
        """
        Initialize the EquityLoader class.
        """
        pass

    def find(self, company_name):
        """
        Search for a company by name on Yahoo Finance and return the results as a DataFrame.

        Args:
            company_name (str): Name of the company to search for.

        Returns:
            pd.DataFrame: A DataFrame containing the search results, or None if no results are found.
        """
        # Yahoo Finance search URL
        url = f"https://fr.finance.yahoo.com/lookup/?s={company_name}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        # Perform HTTP request
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return None

        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.text, "html.parser")
            # Find the results table
            tableau = soup.find("table")

            if tableau:
                # Extract table headers
                en_tetes = [th.text.strip() for th in tableau.find_all("th")]
                # Extract table rows
                lignes = []
                for tr in tableau.find_all("tr")[1:]:  # Skip header row
                    ligne = [td.text.strip() for td in tr.find_all("td")]
                    lignes.append(ligne)

                # Create a DataFrame to display the results
                df = pd.DataFrame(lignes, columns=en_tetes)
                return df
            else:
                print("No table found.")
                return None
        else:
            print(f"Request error: {response.status_code}")
            return None

    def get_historic(self, ticker, period="1d", end=datetime.now().date()):
        """
        Retrieve historical stock data for a given ticker and period.

        Args:
            ticker (str): Stock ticker symbol (e.g., "RNO.PA").
            period (str): Time period for historical data (e.g., "1d", "1mo", "1y").
            end (datetime.date, optional): End date for the data. Defaults to today's date.

        Returns:
            pd.DataFrame: A DataFrame containing the historical stock data.
        """
        try:
            data = yf.download(ticker, end=end, period=period)
            return data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

    
    def get_VIX(self):
        """
        Fetches the latest VIX value.

        Returns:
            float: The latest VIX value as a decimal (e.g., 0.205 for a VIX of 20.5).
        """
        data = self.get_historic(ticker="^VIX")
        if data is not None and not data.empty:
            return float(data.iloc[-1]['Close']) / 100
        return None

    def get_VCAC(self, call=True, T=0):
        return self.get_implied_volatility(ticker_symbol='EWQ', call=call, T=0)

    def get_implied_volatility(self, ticker_symbol, call=True, T=0):
        """
        Fetches the implied volatility for a given ticker's options with an expiration date that exceeds today + T years.

        Args:
            ticker_symbol (str): The ticker symbol of the asset (e.g., "EWQ").
            call (bool, optional): If True, fetches implied volatility for call options.
                                If False, fetches implied volatility for put options.
                                Defaults to True.
            T (float, optional): Number of years to add to the current date to find the minimum expiration date.
                                Defaults to 0.

        Returns:
            float: The implied volatility of the specified ticker's options.
                Returns None if no options data is available or no suitable expiration date is found.
        """
        etf = yf.Ticker(ticker_symbol)
        expirations = etf.options

        if not expirations:
            if ticker_symbol!='EWQ':
                return self.get_VCAC(call=call, T=T)
            else: 
                return None

        # Calculate the target date: today + T years
        target_date = datetime.now() + timedelta(days=T * 365)

        # Find the first expiration date that exceeds the target date
        suitable_expiration = None
        for expiration in expirations:
            expiration_date = datetime.strptime(expiration, "%Y-%m-%d")
            if expiration_date > target_date:
                suitable_expiration = expiration
                break

        if not suitable_expiration:
            suitable_expiration = expirations[0]

        options = etf.option_chain(suitable_expiration)

        if call:
            if not options.calls.empty:
                return options.calls.iloc[0]['impliedVolatility']
        else:
            if not options.puts.empty:
                return options.puts.iloc[0]['impliedVolatility']

        if ticker_symbol!='EWQ':
            return self.get_VCAC(call=call, T=T)
        else: 
            return None
