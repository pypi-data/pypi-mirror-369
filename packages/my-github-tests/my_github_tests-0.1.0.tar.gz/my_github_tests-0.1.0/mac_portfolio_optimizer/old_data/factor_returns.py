import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List


def load_risk_factors_returns(local_path: str) -> pd.DataFrame:
    returns = qis.load_df_from_excel(file_name='Risk Factors Returns', sheet_name='riskfactors',
                                     local_path=local_path)
    mapper = dict(TIER1_CDT='Credit',
                  TIER1_COM='Commodities',
                  TIER1_DM_INFL='Inflation',
                  TIER1_DM_RATES='Rates',
                  TIER1_PEQ='Private Equity',
                  TIER1_REAL='Real Assets',
                  TIER1_WORLD='Equity')
    returns = returns.rename(mapper=mapper, axis=1)
    returns = returns.drop(['Private Equity', 'Real Assets'], axis=1)
    navs = qis.returns_to_nav(returns=returns)
    return navs


import mac_portfolio_optimizer.local_path as lp

local_path = f"{lp.get_resource_path()}"

navs = load_risk_factors_returns(local_path=local_path)

print(navs)

qis.plot_prices_with_dd(prices=navs)

plt.show()


