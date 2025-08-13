"""
check of vol for MAC
"""
import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from qis.models.linear.ewm import compute_ewm_newey_west_vol
from typing import Tuple, Dict
from enum import Enum

# universe data
from mac_portfolio_optimizer.data.excel_loader import load_mac_portfolio_universe
from mac_portfolio_optimizer.data.mac_universe import SaaPortfolio, TaaPortfolio, MacUniverseData

import mac_portfolio_optimizer.local_path as lp
local_path = f"{lp.get_resource_path()}"


def plot_nh_vol(prices: pd.DataFrame) -> None:
    tickers = prices.columns
    with sns.axes_style("darkgrid"):
        fig, axs = plt.subplots(2, 3, figsize=(14, 14), tight_layout=True)
        axs = qis.to_flat_list(axs)
        kwargs = dict(mean_adj_type=qis.MeanAdjType.EWMA, span=24, annualization_factor=4)
        for idx, ticker in enumerate(tickers):
            assets = prices[ticker]
            returns = qis.to_returns(assets, freq='QE', is_log_returns=True).to_frame()
            ewma_vols = qis.compute_ewm_vol(data=returns, **kwargs)
            ewma_nw_vols1, _ = compute_ewm_newey_west_vol(data=returns, num_lags=1, **kwargs)
            ewma_nw_vols2, _ = compute_ewm_newey_west_vol(data=returns, num_lags=2, **kwargs)
            ewma_nw_vols3, _ = compute_ewm_newey_west_vol(data=returns, num_lags=3, **kwargs)
            ewma_nw_vols4, _ = compute_ewm_newey_west_vol(data=returns,  num_lags=4, **kwargs)
            df = pd.concat([ewma_vols.iloc[:, 0].rename('EWM'),
                            ewma_nw_vols1.iloc[:, 0].rename('Newey-West 1'),
                            ewma_nw_vols2.iloc[:, 0].rename('Newey-West 2'),
                            ewma_nw_vols3.iloc[:, 0].rename('Newey-West 3'),
                            ewma_nw_vols4.iloc[:, 0].rename('Newey-West 4')
                            ], axis=1)
            qis.plot_time_series(df=df.loc['31Dec2001':, :],
                                 var_format='{:,.2%}',
                                 title=f"{ticker}",
                                 ax=axs[idx])


def check_ewma_mean(prices: pd.DataFrame, span: int = 24):
    y = qis.to_returns(prices, freq='QE', is_log_returns=True)
    y1 = y - qis.compute_ewm(data=y, span=span)
    y2 = qis.compute_rolling_mean_adj(data=y,
                                     mean_adj_type=qis.MeanAdjType.EWMA,
                                     span=span)
    y3 = y1 - qis.compute_ewm(data=y1, span=span)

    tickers = prices.columns
    with sns.axes_style("darkgrid"):
        fig, axs = plt.subplots(3, len(tickers)//3, figsize=(14, 14), tight_layout=True)
        axs = qis.to_flat_list(axs)
        for idx, ticker in enumerate(tickers):
            df = pd.concat([y1[ticker].rename('EWM1'), y2[ticker].rename('EWM2'), y3[ticker].rename('EWM3')], axis=1)
            if idx < len(axs):
                qis.plot_time_series(df=df.loc['31Dec2004':, :],
                                     var_format='{:,.2%}',
                                     title=f"{ticker}",
                                     ax=axs[idx])


class LocalTests(Enum):
    PLOT_NH_VOL = 1
    CHECK_EMWA_MEAN = 2


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')
    # time_period = qis.TimePeriod('31Dec2022', '31Mar2025')

    import mac_portfolio_optimizer.local_path as lp
    local_path = lp.get_resource_path()

    # load universe
    is_funds_universe = False
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)

    if local_test == LocalTests.PLOT_NH_VOL:
        prices = universe_data.get_joint_prices()
        print(prices.columns)
        tickers = ['Private Equity', 'Private Debt', 'Equity', 'Rates', 'Hedge Funds', 'Commodities Precious']
        plot_nh_vol(prices=prices[tickers])

    elif local_test == LocalTests.CHECK_EMWA_MEAN:
        check_ewma_mean(prices=universe_data.saa_prices)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.CHECK_EMWA_MEAN)
