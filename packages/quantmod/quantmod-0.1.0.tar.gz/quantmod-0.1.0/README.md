
The quantmod package is inspired by the popular R package of the same name but reimagined for the modern Python data stack. It’s designed to support data scientists, analysts, and AI researchers with tools for fast, flexible data exploration and visualization. Whether you're working with time series, building machine learning pipelines, or prototyping data-driven ideas, quantmod offers a clean, intuitive interface that helps you move quickly from data to insight.


## Installation
The easiest way to install quantmod is using pip:

```bash
pip install quantmod
```


## Modules

* [charts](https://kannansingaravelu.com/quantmod/charts/)
* [datasets](https://kannansingaravelu.com/quantmod/datasets/)
* [derivatives](https://kannansingaravelu.com/quantmod/derivatives/)
* [indicators](https://kannansingaravelu.com/quantmod/indicators/)
* [markets](https://kannansingaravelu.com/quantmod/markets/)
* [models](https://kannansingaravelu.com/quantmod/models/)
* [risk](https://kannansingaravelu.com/quantmod/risk/) 
* [timeseries](https://kannansingaravelu.com/quantmod/timeseries/)


## Quickstart

```py
# Retrieves market data & ticker object 
from quantmod.markets import getData, getTicker

# Charting module
import quantmod.charts

# Option price
from quantmod.models import OptionInputs, BlackScholesOptionPricing, MonteCarloOptionPricing

# Risk measures
from quantmod.risk import RiskInputs, ValueAtRisk, ConditionalVaR, VarBacktester

# Calculates price return of different time period.
from quantmod.timeseries import *

# Technical indicators
from quantmod.indicators import ATR

# Derivatives functions
from quantmod.derivatives import maxpain

# Datasets functions
from quantmod.datasets import fetch_historical_data
```
<br>
Note: quantmod is currently under active development, and anticipate ongoing enhancements and additions. The aim is to continually improve the package and expand its capabilities to meet the evolving needs of the community.


## Examples
Refer to the [examples](https://kannansingaravelu.com/) section for more details.


## Changelog
The list of changes to quantmod between each release can be found [here](https://kannansingaravelu.com/quantmod/changelog/)


## Community
[Join the quantmod server](https://discord.com/invite/DXQyezbJ) to share feature requests, report bugs, and discuss the package.


## Legal 
`quatmod` is distributed under the **Apache Software License**. See the [LICENSE.txt](https://www.apache.org/licenses/LICENSE-2.0.txt) file in the release for details.
