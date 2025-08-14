import pandas as pd
import numpy as np
from jugaad_data.nse import NSELive


# construct a class object
class OptionChain:
    """
    A class to fetch and process option chain data from NSE (National Stock Exchange).

    Parameters
    ----------
    symbol : str
        Trading symbol (e.g., 'NIFTY', 'BANKNIFTY' or any equity symbol)
    expiry_date : str
        Expiry date of the options

    Attributes
    ----------
    option_chain : pandas.DataFrame
        Processed option chain data
    call_option_data : pandas.DataFrame
        Call options data
    put_option_date : pandas.DataFrame
        Put options data
    option_pain : float
        Maximum pain strike price

    Methods
    -------
    get_option_price()
        Get the option price (last traded, bid, or ask) for a specific option
    get_synthetic_futures()
        Calculate synthetic futures price for a given strike price
    """

    def __init__(self, symbol, expiry_date):
        self.n = NSELive()
        self.symbol = symbol
        self.expiry_date = expiry_date

        # flatten json and convert to dataframe
        if symbol in ["NIFTY", "BANKNIFTY"]:
            df = self.n.index_option_chain(self.symbol)["records"]["data"]
        else:
            df = self.n.equities_option_chain(self.symbol)["records"]["data"]
        df = pd.json_normalize(df).fillna(0)
        self.df = df[df["expiryDate"] == self.expiry_date]

        # the __dict__ attributes
        self.option_chain = self._get_option_chain()
        self.call_option_data = self._get_call_option_data()
        self.put_option_data = self._get_put_option_data()
        self.option_pain = self._get_option_pain()

    # get option chain
    def _get_option_chain(self):
        """
        Retrieve the complete option chain data.

        Returns
        -------
        pandas.DataFrame
            Complete option chain data for the specified symbol and expiry
        """
        return self.df

    # Create function to get call and put options
    def _get_call_option_data(self):
        """
        Extract and process call option data from the option chain.

        Returns
        -------
        pandas.DataFrame
            Processed call options data with simplified column names
        """
        calls = self.option_chain.iloc[:, 21:].reset_index(drop=True)
        cols = [i[3:] for i in calls.columns]
        calls.columns = cols
        return calls

    def _get_put_option_data(self):
        """
        Extract and process put option data from the option chain.

        Returns
        -------
        pandas.DataFrame
            Processed put options data with simplified column names
        """
        puts = self.option_chain.iloc[:, 2:21].reset_index(drop=True)
        cols = [i[3:] for i in puts.columns]
        puts.columns = cols
        return puts

    # get option price
    def get_option_price(self, strike, opt_type, txn_type=None):
        """
        Get the option price (last traded, bid, or ask) for a specific option.

        Parameters
        ----------
        strike : float
            Strike price of the option
        opt_type : str
            Option type ('CE' for Call or 'PE' for Put)
        txn_type : str, optional
            Transaction type ('buy', 'sell', or None for last price)

        Returns
        -------
        float
            Option price based on the specified parameters
        """
        price_type = (
            "bidprice"
            if txn_type == "sell"
            else "askPrice"
            if txn_type == "buy"
            else "lastPrice"
        )
        col = f"{opt_type}.{price_type}"

        return float(self.df[self.df["strikePrice"] == strike][col].iloc[0])

    # get synthetic futures
    def get_synthetic_futures(self, strike):
        """
        Calculate synthetic futures price for a given strike price.
        Synthetic Futures price = Strike + Call - Put

        Parameters
        ----------
        strike : float
            Strike price for which to calculate synthetic futures

        Returns
        -------
        float
            Synthetic futures price
        """
        return (
            strike
            + self.get_option_price(strike, opt_type="CE", txn_type="buy")
            - self.get_option_price(strike, opt_type="PE", txn_type="sell")
        )

    def _get_option_pain(self) -> float:
        """
        Calculate the maximum pain point - the strike price where the total value of all
        options (calls and puts) would cause the most financial pain to option writers.

        Returns
        -------
        float
            Strike price at which maximum pain occurs
        """
        # Get data from class attributes
        strikes = np.array(self.option_chain["strikePrice"], dtype=float)
        call_oi = np.array(self.call_option_data["openInterest"], dtype=float)
        put_oi = np.array(self.put_option_data["openInterest"], dtype=float)

        # Calculate pain for each possible expiry price
        total_pain = []

        for expiry_price in strikes:
            # Calculate call options pain
            call_pain = sum(
                call_oi[i] * max(0, expiry_price - strike)
                for i, strike in enumerate(strikes)
            )

            # Calculate put options pain
            put_pain = sum(
                put_oi[i] * max(0, strike - expiry_price)
                for i, strike in enumerate(strikes)
            )

            # Total pain at this price level
            total_pain.append(call_pain + put_pain)

        # Find strike with minimum pain
        max_pain_index = np.argmin(total_pain)
        return float(strikes[max_pain_index])

    def plot_pain_analysis(self):
        """
        Plot pain analysis for the option chain.
        """
        # Get data from class attributes
        strikes = np.array(self.option_chain["strikePrice"], dtype=float)
        call_oi = np.array(self.call_option_data["openInterest"], dtype=float)
        put_oi = np.array(self.put_option_data["openInterest"], dtype=float)

        results = []

        for expiry_price in strikes:
            # Calculate call options pain
            call_pain = sum(
                call_oi[i] * max(0, expiry_price - strike)
                for i, strike in enumerate(strikes)
            )

            # Calculate put options pain
            put_pain = sum(
                put_oi[i] * max(0, strike - expiry_price)
                for i, strike in enumerate(strikes)
            )

            results.append(
                {
                    "Strike": expiry_price,
                    "Call Pain": call_pain,
                    "Put Pain": put_pain,
                    "Total Pain": call_pain + put_pain,
                }
            )

        analysis = pd.DataFrame(results)
        # Plot the pain distribution (requires matplotlib)
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 6))
            plt.plot(
                analysis["Strike"], analysis["Total Pain"], "b-", label="Total Pain"
            )
            plt.plot(
                analysis["Strike"], analysis["Call Pain"], "g--", label="Call Pain"
            )
            plt.plot(analysis["Strike"], analysis["Put Pain"], "r--", label="Put Pain")
            plt.axvline(
                x=self._get_option_pain(),
                color="k",
                linestyle=":",
                label=f"Max Pain Strike: {self._get_option_pain():}",
            )

            plt.title("Option Pain Analysis")
            plt.xlabel("Strike Price")
            plt.ylabel("Pain Value")
            plt.legend()
            plt.grid(True)

        except ImportError:
            print("\nMatplotlib not installed. Skipping plot generation.")

        plt.show()
