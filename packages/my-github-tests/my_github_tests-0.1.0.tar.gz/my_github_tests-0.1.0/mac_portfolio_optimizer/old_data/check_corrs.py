
import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict
from enum import Enum

# universe data
from mac_portfolio_optimizer.data.excel_loader import load_mac_portfolio_universe
from mac_portfolio_optimizer.data.mac_universe import SaaPortfolio, TaaPortfolio

import mac_portfolio_optimizer.local_path as lp

local_path = f"{lp.get_resource_path()}"
local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
# local_path_out = lp.get_output_path()

universe_data = load_mac_portfolio_universe(local_path=local_path,
                                            saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                            taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)

prices = universe_data.saa_prices

covars = qis.estimate_rolling_ewma_covar(prices=prices,
                                         returns_freq='ME',
                                         rebalancing_freq='YE',
                                         span=36,
                                         demean=True,
                                         apply_an_factor=True)
for date, covar in covars.items():
    print(date)
    norm_to_corr = 1.0 / np.sqrt(np.diag(covar.to_numpy()))
    corr = covar * np.outer(norm_to_corr, norm_to_corr)
    print(corr)

