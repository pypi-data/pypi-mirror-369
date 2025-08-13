"""
each factor is constructed as portfolio with long-term vol factor of 10%
"""
import typing

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import qis as qis
from typing import Optional, Tuple, Union
from qis import TimePeriod
from enum import Enum

import mac_portfolio_optimizer.local_path as lp


TIME_PERIOD = qis.TimePeriod('31Dec2004', '08Aug2025')


class RiskFactors(str, Enum):
    EQUITY = 'Equity'
    BOND = 'Bond'
    CREDIT = 'Credit'
    PE = 'PE premia'
    LIQ = 'Liquidity premia'
    INFLATION = 'Inflation premia'


def compute_equity_factor(futures_prices: pd.DataFrame,
                          is_portfolio_vol_target: bool = True,
                          rebalancing_freq: str = 'QE',
                          portfolio_vol_target: float = 0.15,
                          vol_span: int = 3*52,
                          verbouse: bool = False
                          ) -> pd.Series:
    prices = futures_prices[['NDDUWI']]
    strategic_weights = np.array([1.0])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.EQUITY.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbouse:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_bond_factor(futures_prices: pd.DataFrame,
                        is_portfolio_vol_target: bool = True,
                        rebalancing_freq: str = 'ME',
                        portfolio_vol_target: float = 0.15,
                        vol_span: int = 3*52,
                        verbouse: bool = False
                        ) -> pd.Series:

    prices = futures_prices[['TY1', 'RX1', 'G1', 'JB1', 'CN1', 'XM1']]
    strategic_weights = np.array([0.6, 0.1, 0.1, 0.1, 0.05, 0.05])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.BOND.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbouse:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_credit_factor(futures_prices: pd.DataFrame,
                          is_portfolio_vol_target: bool = True,
                          rebalancing_freq: str = 'ME',
                          portfolio_vol_target: float = 0.15,
                          vol_span: int = 3*52,
                          verbouse: bool = False
                          ) -> pd.Series:
    prices = futures_prices[['IG', 'CDX']]
    strategic_weights = np.array([0.66, 0.34])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.CREDIT.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbouse:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return factor


def compute_pe_premia_factor(futures_prices: pd.DataFrame,
                             is_portfolio_vol_target: bool = True,
                             rebalancing_freq: str = 'ME',
                             portfolio_vol_target: float = 0.15,
                             vol_span: int = 3*52,
                             verbouse: bool = False
                             ) -> pd.Series:
    #futures_prices = load_base_futures_prices()[['NQ1 Index', 'ES1 Index']].dropna()
    #strategic_weights = np.array([1.0, -1.0])
    # futures_prices = load_base_futures_prices()[['NQ1', 'RTY1', 'SPW']].dropna()
    # strategic_weights = np.array([0.5, 0.5, -1.0])
    #prices = futures_prices[['NQ1', 'RTY', 'CDX', 'ES1']]
    #strategic_weights = np.array([0.5, 0.5, 1.0, -1.0])
    #prices = futures_prices[['NQ1', 'RTY',  'ES1']]
    #strategic_weights = np.array([0.5, 0.5, -1.0])
    #prices = futures_prices[['NQ1', 'CDX', 'ES1']] #best so far
    #strategic_weights = np.array([1.0, 1.0, -1.0])
    prices = futures_prices[['NQ1', 'RTY', 'CDX', 'NDDUWI']]
    strategic_weights = np.array([0.5, 0.5, 1.0, -1.0])

    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.PE.value)
    factor = portfolio_data.get_portfolio_nav()
    #if verbouse:
    qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return portfolio_data.get_portfolio_nav()


def compute_liquidity_premia_factor(futures_prices: pd.DataFrame,
                                    verbouse: bool = True,
                                    is_portfolio_vol_target: bool = True,
                                    rebalancing_freq: str = 'ME',
                                    portfolio_vol_target: float = 0.15,
                                    vol_span: int = 3*52
                                    ) -> pd.Series:

    prices = futures_prices[['FF1', 'SFR1', 'JPY', 'AUD', 'IG', 'CDX', 'GLD']]
    strategic_weights = np.array([10.0, -10.0, 0.5, -0.5, -4.0, -1.0, 0.33])
    strategic_weights = -1.0*strategic_weights
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.LIQ.value)
    factor = portfolio_data.get_portfolio_nav()
    if verbouse:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
        figs = qis.generate_strategy_factsheet(portfolio_data=portfolio_data,
                                               benchmark_prices=futures_prices['ES1'],
                                               time_period=TIME_PERIOD,
                                               add_current_position_var_risk_sheet=True,
                                               **qis.fetch_default_report_kwargs(time_period=TIME_PERIOD))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"{RiskFactors.LIQ.value}_portfolio",
                             local_path=lp.get_output_path())
    return factor


def compute_inflation_premia_factor(futures_prices: pd.DataFrame,
                                    verbouse: bool = True,
                                    is_portfolio_vol_target: bool = True,
                                    rebalancing_freq: str = 'ME',
                                    portfolio_vol_target: float = 0.15,
                                    vol_span: int = 3*52
                                    ) -> pd.Series:

    prices = futures_prices[['CRY']]
    strategic_weights = np.array([1.0])
    portfolio_data = compute_risk_factor_portfolio(prices=prices,
                                                   strategic_weights=strategic_weights,
                                                   rebalancing_freq=rebalancing_freq,
                                                   portfolio_vol_target=portfolio_vol_target,
                                                   is_portfolio_vol_target=is_portfolio_vol_target,
                                                   vol_span=vol_span,
                                                   ticker=RiskFactors.INFLATION.value)    
    factor = portfolio_data.get_portfolio_nav()
    if verbouse:
        qis.plot_prices_with_dd(prices=factor, time_period=TIME_PERIOD)
    return portfolio_data.get_portfolio_nav()


def load_base_futures_prices() -> pd.DataFrame:
    """
    Load risk prices data. Data is generated only once and cached for subsequent calls.
    Returns the same DataFrame instance on every call after the first.
    """
    if not hasattr(load_base_futures_prices, '_cache'):
        load_base_futures_prices._cache = qis.load_df_from_csv(file_name='futures_prices',
                                                               local_path=lp.get_resource_path()).loc['31Dec1999': ]
    return load_base_futures_prices._cache


def load_mac_prices() -> Tuple[pd.DataFrame, pd.DataFrame]:
    local_path = "/mac_portfolio_optimizer/resources//"
    prices = qis.load_df_from_excel(file_name="mac_prices", sheet_name="prices", local_path=local_path)
    prices_unsmoothed = qis.load_df_from_excel(file_name="mac_prices", sheet_name="prices_unsmoothed", local_path=local_path)
    return prices, prices_unsmoothed


def load_rates() -> pd.Series:
    rate = qis.load_df_from_csv(file_name="rate", local_path=lp.get_resource_path())
    return rate.iloc[:, 0]


def compute_pe_excess_performance(is_unsmoothed: Optional[bool] = None) -> Union[pd.DataFrame, pd.Series]:
    prices, prices_unsmoothed = load_mac_prices()
    pe_reported = prices['Private Equity'].asfreq('QE')
    pe_unsmoothed = prices_unsmoothed['Private Equity'].asfreq('QE')
    if is_unsmoothed is None:
        df = pd.concat([pe_reported.rename('reported'), pe_unsmoothed.rename('unsmoothed')], axis=1)
    elif is_unsmoothed:
        df = pe_unsmoothed.rename('unsmoothed')
    else:
        df = pe_reported.rename('reported')
    returns = qis.to_returns(prices=df)
    excess_returns = qis.compute_excess_returns(returns=returns, rates_data = load_rates())
    return excess_returns


def analyse_pe_equity(is_unsmoothed: bool = True, verbouse: bool = False):
    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')
    pe_excess_returns = compute_pe_excess_performance(is_unsmoothed=is_unsmoothed)
    futures_prices = load_base_futures_prices()
    pe_premia_nav = compute_pe_premia_factor(futures_prices=futures_prices, portfolio_vol_target=0.15, rebalancing_freq='QE')

    equity_returns = futures_prices['ES1'].reindex(index=pe_excess_returns.index).ffill().pct_change()
    pe_ex_equity = pe_excess_returns.subtract(equity_returns)

    # x = pd.concat([pe_premia_nav, futures_prices['ES1']], axis=1)
    x = pe_premia_nav
    x = qis.to_returns(prices=x, freq='QE', is_log_returns=False).reindex(index=pe_ex_equity.index)

    ewm_linear_model = qis.EwmLinearModel(x=x, y=pe_ex_equity)
    ewm_linear_model.fit(span=20, is_x_correlated=True, mean_adj_type=qis.MeanAdjType.NONE)

    betas = ewm_linear_model.get_asset_factor_betas()
    betas[pe_premia_nav.name] = 0.3 + 0.7*betas[pe_premia_nav.name]
    joint_attrib = compute_benchmarks_beta_attribution_from_returns(portfolio_returns=pe_ex_equity,
                                                                    benchmark_returns=x,
                                                                    portfolio_benchmark_betas=betas,
                                                                    residual_name='residual',
                                                                    time_period=time_period)

    if verbouse:
        with sns.axes_style("darkgrid"):
            fig, axs = plt.subplots(3, 1, figsize=(12, 12), tight_layout=True)
            returns = pd.concat([pe_excess_returns.rename('pe excess return'),
                                 pe_ex_equity.rename('pe ex equity'),
                                 x
                                 ], axis=1)
            returns = time_period.locate(returns)
            qis.plot_time_series(df=returns.cumsum(0),
                                 var_format='{:,.2f}',
                                 legend_stats=qis.LegendStats.AVG_NONNAN_LAST,
                                 title=f"{pe_premia_nav.name} returns",
                                 ax=axs[0])
            qis.plot_time_series(df=time_period.locate(betas),
                                 var_format='{:,.2f}',
                                 legend_stats=qis.LegendStats.AVG_NONNAN_LAST,
                                 title=f"{pe_premia_nav.name} betas",
                                 ax=axs[1])
            qis.plot_time_series(df=joint_attrib.cumsum(0),
                                 var_format='{:,.0%}',
                                 legend_stats=qis.LegendStats.LAST_NONNAN,
                                 title=f"{pe_premia_nav.name} attribution",
                                 ax=axs[2])


def compute_risk_factor_portfolio(prices: pd.DataFrame,
                                  strategic_weights: np.ndarray,
                                  rebalancing_freq: str = 'QE',
                                  portfolio_vol_target: float = 0.15,
                                  vol_span: int = 3*52,
                                  is_portfolio_vol_target: bool = True,
                                  ticker: str = 'factor'
                                  ) -> qis.PortfolioData:
    if is_portfolio_vol_target:
        risk_weights = compute_volatility_targeted_portfolio(prices=prices,
                                                             strategic_weights=strategic_weights,
                                                             rebalancing_freq=rebalancing_freq,
                                                             portfolio_vol_target=portfolio_vol_target,
                                                             vol_span=vol_span)
    else:
        risk_weights = strategic_weights
    portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                  weights=risk_weights,
                                                  ticker=ticker,
                                                  rebalancing_freq=rebalancing_freq)
    return portfolio_data


def compute_volatility_targeted_portfolio(prices: pd.DataFrame,
                                          strategic_weights: np.ndarray,
                                          returns_freq: str = 'W-WED',
                                          vol_span: int = 3*52,
                                          portfolio_vol_target: float = 0.15,
                                          rebalancing_freq: str = 'ME'
                                          ) -> pd.DataFrame:
    returns = qis.to_returns(prices=prices, freq=returns_freq, is_log_returns=True)
    strategic_weights = pd.DataFrame(qis.np_array_to_df_index(strategic_weights, n_index=len(returns.index)),
                                     index=returns.index, columns=returns.columns)
    portfolio_vol = qis.compute_portfolio_vol(returns=returns,
                                              weights=strategic_weights,
                                              span=vol_span,
                                              annualize=True)
    instrument_portfolio_leverages = portfolio_vol_target * qis.to_finite_reciprocal(data=portfolio_vol)
    risk_weights = strategic_weights.multiply(instrument_portfolio_leverages, axis=0)
    risk_weights = risk_weights.resample(rebalancing_freq).last()
    return risk_weights


def compute_benchmarks_beta_attribution_from_returns(portfolio_returns: pd.Series,
                                                    benchmark_returns: pd.DataFrame,
                                                    portfolio_benchmark_betas: pd.DataFrame,
                                                    residual_name: str = 'Alpha',
                                                    time_period: TimePeriod = None
                                                    ) -> pd.DataFrame:
    # to be replaced with qis
    if isinstance(benchmark_returns, pd.Series):
        benchmark_returns = benchmark_returns.to_frame()
    benchmark_returns = benchmark_returns.reindex(index=portfolio_returns.index)
    x_attribution = (portfolio_benchmark_betas.shift(1)).multiply(benchmark_returns)
    total_attrib = x_attribution.sum(axis=1)
    residual = np.subtract(portfolio_returns, total_attrib)
    joint_attrib = pd.concat([x_attribution, residual.rename(residual_name)], axis=1)
    if time_period is not None:
        joint_attrib = time_period.locate(joint_attrib)
        joint_attrib.iloc[0, :] = 0.0
    return joint_attrib


def compute_excess_return_navs(prices: Union[pd.Series, pd.DataFrame],
                               rates_data: pd.Series,
                               first_date: pd.Timestamp = None
                               ) -> Union[pd.Series, pd.DataFrame]:
    # to be replaced with qis
    returns = qis.to_returns(prices=prices, is_first_zero=True)
    excess_returns = qis.compute_excess_returns(returns=returns, rates_data=rates_data)
    navs = qis.returns_to_nav(returns=excess_returns, first_date=first_date)
    return navs


@qis.timer
def compute_risk_factors(is_portfolio_vol_target: bool = True,
                         rebalancing_freq: str = 'ME',
                         portfolio_vol_target: float = 0.15,
                         vol_span: int = 3*52,
                         verbouse: bool = False
                         ) -> pd.DataFrame:
    futures_prices = load_base_futures_prices()
    kwargs = dict(is_portfolio_vol_target=is_portfolio_vol_target,
                  rebalancing_freq=rebalancing_freq,
                  portfolio_vol_target=portfolio_vol_target,
                  vol_span=vol_span,
                  verbouse=verbouse)
    risk_factors = pd.concat([compute_equity_factor(futures_prices=futures_prices, **kwargs),
                              compute_bond_factor(futures_prices=futures_prices, **kwargs),
                              compute_credit_factor(futures_prices=futures_prices, **kwargs),
                              compute_pe_premia_factor(futures_prices=futures_prices, **kwargs),
                              compute_liquidity_premia_factor(futures_prices=futures_prices, **kwargs),
                              compute_inflation_premia_factor(futures_prices=futures_prices, **kwargs)
                              ], axis=1)
    return risk_factors


class LocalTests(Enum):
    GENERATE_BBG_PRICES = 1
    MAC_PRICES = 2
    PE_PREMIA = 4
    LIQUIDITY_PREMIA = 5
    FACTOR_PRICES = 6


def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """

    # print(futures_prices)
    if local_test == LocalTests.GENERATE_BBG_PRICES:
        from bbg_fetch import fetch_field_timeseries_per_tickers

        # 1. generate rates data
        rate = fetch_field_timeseries_per_tickers(tickers={'USGG3M Index': '3m_rate'}, freq='B').ffill().iloc[:, 0] / 100.0

        # SPW is LWE1 Index
        tickers = {# equity indices
                   'SPW Index': 'SPW',  # ew s&p500
                   'NDDUWI Index': 'NDDUWI',
                   'RTY Index': 'RTY',
                   # equity futures
                   'ES1 Index': 'ES1',
                   'NQ1 Index': 'NQ1',
                   'ZWP1 Index': 'ZWP1',  # NDDUWI # need backfill
                   'LWE1 Index': 'LWE1',  # ew s&p500 # need backfill
                   'RTY1 Index': 'RTY1',
                   # bond futures
                   'TY1 Comdty': 'TY1',
                   'RX1 Comdty': 'RX1',
                   'G 1 Comdty': 'G1',
                   'JB1 Comdty': 'JB1',
                   'CN1 Comdty': 'CN1',
                   'XM1 Comdty': 'XM1',
                   # rates
                   'SFR1 Comdty': 'SFR1',
                   'ED5 Comdty': 'ED1',
                   'FF1 Comdty': 'FF1',
                   # credit trackers
                   'LBUSTRUU Index': 'IG cash',
                   'LF98TRUU Index': 'HY cash',
                   'UISYMI5S Index': 'IG',
                   'UISYMH5S Index': 'CDX',
                   # fx
                   'JY1 Curncy': 'JPY',
                   'AD1 Curncy': 'AUD',
                   # commodities
                   'GC1 Comdty': 'GLD',
                   'CRY Index': 'CRY',
                   'BCOM Index': 'BCOM',
                   }
        prices = fetch_field_timeseries_per_tickers(tickers=tickers, freq='B').ffill()

        # backfill SPW
        prices['SPW'] = qis.bfill_timeseries(df_newer=prices['LWE1'].loc['2024':],
                                              df_older=compute_excess_return_navs(prices=prices['SPW'], rates_data=rate),
                                              is_prices=True)

        # backfill NDDUWI
        prices['NDDUWI'] = qis.bfill_timeseries(df_newer=prices['ZWP1'],
                                              df_older=compute_excess_return_navs(prices=prices['NDDUWI'], rates_data=rate),
                                              is_prices=True)
        # backfill rty
        prices['RTY'] = qis.bfill_timeseries(df_newer=prices['RTY1'],
                                              df_older=compute_excess_return_navs(prices=prices['RTY'], rates_data=rate),
                                              is_prices=True)
        # backfill sofr
        prices['SFR1'] = qis.bfill_timeseries(df_newer=prices['SFR1'], df_older=prices['ED1'], is_prices=True)

        # backfill IG
        prices['IG'] = qis.bfill_timeseries(df_newer=prices['IG'],
                                              df_older=compute_excess_return_navs(prices=prices['IG cash'], rates_data=rate),
                                              is_prices=True)

        # backfill CDX
        prices['CDX'] = qis.bfill_timeseries(df_newer=prices['CDX'],
                                              df_older=compute_excess_return_navs(prices=prices['HY cash'], rates_data=rate),
                                              is_prices=True)

        prices = prices.drop(['ED1', 'LWE1', 'ZWP1', 'RTY1', 'IG cash', 'HY cash'], axis=1)

        # backfill cdx and ig
        #prices['CDX'] = prices['CDX'].ffill().bfill()
        #prices['IG'] = prices['IG'].ffill().bfill()

        qis.plot_prices_with_dd(prices.loc['31Dec1999':, :], framealpha=0.9)

        qis.save_df_to_csv(df=prices, file_name='futures_prices', local_path=lp.get_resource_path())
        qis.save_df_to_csv(df=rate.to_frame(), file_name='rate', local_path=lp.get_resource_path())

    elif local_test == LocalTests.MAC_PRICES:
        prices, prices_unsmoothed = load_mac_prices()
        print(prices)
        print(prices.columns)

    elif local_test == LocalTests.PE_PREMIA:
        # get_pe_performance()
        # estimate_pe_premia(verbouse=True)
        analyse_pe_equity(verbouse=True)

    elif local_test == LocalTests.LIQUIDITY_PREMIA:
        # get_pe_performance()
        futures_prices = load_base_futures_prices()
        compute_liquidity_premia_factor(futures_prices=futures_prices, verbouse=True)

    elif local_test == LocalTests.FACTOR_PRICES:
        factors = compute_risk_factors()
        print(factors)
        fig = qis.generate_multi_asset_factsheet(prices=factors,
                                                 benchmark='Equity',
                                                 time_period=TIME_PERIOD,
                                                 **qis.fetch_default_report_kwargs(time_period=TIME_PERIOD, add_rates_data=False))
        qis.save_figs_to_pdf(figs=[fig],
                             file_name=f"risk_factors",
                             local_path=lp.get_output_path())
        qis.save_df_to_csv(df=factors, file_name='futures_risk_factors', local_path=lp.get_resource_path())

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.FACTOR_PRICES)
