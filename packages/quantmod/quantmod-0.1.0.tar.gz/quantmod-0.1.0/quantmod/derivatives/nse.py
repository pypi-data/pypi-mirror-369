# improvised from nsepython
# to be used only for tutorial purposes
# for production use, please reach out to NSE India
import os, sys
import requests
import numpy as np
import pandas as pd
import json
import random
import datetime, time
import logging
import re
import urllib.parse

# Constants
indices = ["NIFTY", "FINNIFTY", "BANKNIFTY"]

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,en-IN;q=0.8,en-GB;q=0.7",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
}

# Curl headers
curl_headers = """ -H "authority: beta.nseindia.com" -H "cache-control: max-age=0" -H "dnt: 1" -H "upgrade-insecure-requests: 1" -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36" -H "sec-fetch-user: ?1" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" -H "sec-fetch-site: none" -H "sec-fetch-mode: navigate" -H "accept-encoding: gzip, deflate, br" -H "accept-language: en-US,en;q=0.9,hi;q=0.8" --compressed"""

# https://ipapi.co/json
# https://ipinfo.io/json

try:
    # Try ipapi.co
    response = requests.get("https://ipapi.co/json/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        country_code = data.get('country_code', '').upper()
        mode = "local" if country_code == "IN" else "vpn"
    else:
        # Fallback to ipinfo.io
        response = requests.get("https://ipinfo.io/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            country_code = data.get('country', '').upper()
            mode = "local" if country_code == "IN" else "vpn"
        else:
            mode = "local"
            
except Exception:
    mode = "local"


def nsefetch(payload):
    if mode == "vpn":
        if ("%26" in payload) or ("%20" in payload):
            encoded_url = payload
        else:
            encoded_url = urllib.parse.quote(payload, safe=":/?&=")
        payload_var = 'curl -b cookies.txt "' + encoded_url + '"' + curl_headers + ""
        try:
            output = os.popen(payload_var).read()
            output = json.loads(output)
        except ValueError:  # includes simplejson.decoder.JSONDecodeError:
            payload2 = "https://www.nseindia.com"
            output2 = os.popen(
                'curl -c cookies.txt "' + payload2 + '"' + curl_headers + ""
            ).read()

            output = os.popen(payload_var).read()
            output = json.loads(output)
        return output

    else: # mode == "local":
        try:
            output = requests.get(payload, headers=headers).json()
            # print(output)
        except ValueError:
            s = requests.Session()
            try:
                output = s.get("http://nseindia.com/option-chain", headers=headers)
                output = s.get(payload, headers=headers).json()
            except ValueError:
                output = s.get("https://www.nseindia.com", headers=headers)
                output = output.json()
            # output = s.get("https://www.nseindia.com/option-chain", headers=headers) # replaced http://nseindia.com with https://www.nseindia.com/option-chain
            output = s.get(payload, headers=headers).json()
        return output


class OptionData:
    """
    A class to fetch and analyze option chain data from NSE.

    Parameters
    ----------
    symbol : str
        Trading symbol of the stock/index (e.g., 'NIFTY', 'RELIANCE')
    expiry_dt : str
        Expiry date in format '%d-%b-%Y' (e.g., '27-Mar-2025')
        Note: Month should be first 3 letters capitalized (Jan, Feb, Mar, etc.)

    Attributes
    ----------
    get_put_call_ratio : float
        Put-Call ratio based on open interest
    get_maximum_pain_strike : float
        Maximum pain strike price
    get_call_option_data : pandas.DataFrame
        Call option chain data
    get_put_option_data : pandas.DataFrame
        Put option chain data

    Methods
    -------
    get_option_quote : float
        Get option quote for specific strike price, option type and transaction intent
    get_synthetic_future_price : float
        Calculate synthetic futures price using put-call parity
    """

    def __init__(self, symbol, expiry_dt):
        """
        Initialize the OptionData class.

        Parameters
        ----------
        symbol : str
            Trading symbol of the stock/index (e.g., 'NIFTY', 'RELIANCE')
        expiry_dt : str
            Expiry date in format '%d-%b-%Y' (e.g., '27-Mar-2025')
            Note: Month should be first 3 letters capitalized (Jan, Feb, Mar, etc.)
        """
        self.expiry_dt = expiry_dt
        self.symbol = symbol.replace(
            "&", "%26"
        )  # URL Parse for Stocks Like M&M Finance
        self.payload = self._nse_optionchain_scrapper()

        self.get_put_call_ratio = self._get_option_pcr()
        self.get_maximum_pain_strike = self._get_maximum_pain_strike()
        self.get_call_option_data = self._get_call_option_data()
        self.get_put_option_data = self._get_put_option_data()

    def _nse_optionchain_scrapper(self):
        """
        Fetch option chain data from NSE website.

        Returns
        -------
        dict
            Raw option chain data from NSE API
        """
        if any(x in self.symbol for x in indices):
            payload = nsefetch(
                "https://www.nseindia.com/api/option-chain-indices?symbol="
                + self.symbol
            )
        else:
            payload = nsefetch(
                "https://www.nseindia.com/api/option-chain-equities?symbol="
                + self.symbol
            )
        return payload

    def get_option_quote(self, strikePrice, optionType, intent=""):
        """
        Get option quote for specific strike price and option type.

        Parameters
        ----------
        strikePrice : float
            Strike price of the option
        optionType : str
            Type of option, either 'CE' (Call) or 'PE' (Put)
        intent : str, optional
            Quote type:
            - '' (default) for last traded price
            - 'sell' for bid price
            - 'buy' for ask price

        Returns
        -------
        float
            Option price based on the specified intent
        """
        for x in range(len(self.payload["records"]["data"])):
            if (self.payload["records"]["data"][x]["strikePrice"] == strikePrice) & (
                self.payload["records"]["data"][x]["expiryDate"] == self.expiry_dt
            ):
                if intent == "":
                    return self.payload["records"]["data"][x][optionType]["lastPrice"]
                if intent == "sell":
                    return self.payload["records"]["data"][x][optionType]["bidprice"]
                if intent == "buy":
                    return self.payload["records"]["data"][x][optionType]["askPrice"]

    def _get_option_pcr(self):
        """
        Calculate Put-Call Ratio based on open interest.

        Returns
        -------
        float
            Put-Call ratio rounded to 2 decimal places
        """
        ce_oi = 0
        pe_oi = 0
        for i in self.payload["records"]["data"]:
            if i["expiryDate"] == self.expiry_dt:
                try:
                    ce_oi += i["CE"]["openInterest"]
                    pe_oi += i["PE"]["openInterest"]
                except KeyError:
                    pass
        return round(pe_oi / ce_oi, 2)

    def get_synthetic_future_price(self, strike):
        """
        Calculate synthetic futures price using put-call parity.

        Parameters
        ----------
        strike : float
            Strike price to use for calculation

        Returns
        -------
        float
            Synthetic futures price
        """
        synthetic_futures = (
            strike
            + self.get_option_quote(strike, "CE", "buy")
            - self.get_option_quote(strike, "PE", "sell")
        )
        return synthetic_futures

    def _get_call_option_data(self):
        """
        Get call options data for current expiry.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing call options data sorted by strike price
        """
        ce_values = [
            data["CE"]
            for data in self.payload["records"]["data"]
            if "CE" in data and data["expiryDate"] == self.expiry_dt
        ]
        return pd.DataFrame(ce_values).sort_values(["strikePrice"])

    def _get_put_option_data(self):
        """
        Get put options data for current expiry.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing put options data sorted by strike price
        """
        pe_values = [
            data["PE"]
            for data in self.payload["records"]["data"]
            if "PE" in data and data["expiryDate"] == self.expiry_dt
        ]
        return pd.DataFrame(pe_values).sort_values(["strikePrice"])

    def _get_maximum_pain_strike(self):
        """
        Calculate maximum pain strike price.

        Returns
        -------
        float
            Strike price where maximum pain occurs
        """
        calls = self._get_call_option_data()
        strikes = calls["strikePrice"]
        ce_oi = calls["openInterest"]
        pe_oi = self._get_put_option_data()["openInterest"]

        total_pain = [
            sum(ce_oi * np.maximum(0, expiry_price - strikes))
            + sum(pe_oi * np.maximum(0, strikes - expiry_price))
            for expiry_price in strikes
        ]

        return strikes[np.argmin(total_pain)]
