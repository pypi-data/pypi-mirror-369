"""
figures for MAS optimisation paper
"""
import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List
from enum import Enum

from optimalportfolios import (LassoModelType, LassoModel, solve_lasso_cvx_problem,
                               adjust_returns_with_ar1, compute_ar1_unsmoothed_prices)

# universe data
from mac_portfolio_optimizer.data.excel_loader import load_mac_portfolio_universe
from mac_portfolio_optimizer.data.mac_universe import SaaPortfolio, TaaPortfolio, MacUniverseData


def compute_lags_x(y: pd.Series, num_of_lags: int = 2) -> pd.DataFrame:
    x = {}
    for n in np.arange(1, num_of_lags+1):
        x[f"lag-{n}"] = y.shift(n)
    x = pd.DataFrame.from_dict(x, orient='columns')
    return x


def estimate_ar_p_process_with_lasso(y: pd.Series,
                                     lasso_model: LassoModel,
                                     num_of_lags: int = 2,
                                     verbose: bool = True
                                     ) -> pd.Series:
    """
    estimate ar process y_{t} = alpha + b_1*y_{t-1} + b_2*y_{t-2} ... using lasso
    """
    if lasso_model.demean:
        y = y - qis.compute_ewm(data=y, span=lasso_model.span)
    x = compute_lags_x(y=y, num_of_lags=num_of_lags)
    b, alpha, r2 = solve_lasso_cvx_problem(x=x.to_numpy(),
                                           y=y.to_frame().to_numpy(),
                                           reg_lambda=lasso_model.reg_lambda,
                                           span=lasso_model.span,
                                           nonneg=True,
                                           is_declining=True)
    b = b.reshape(1, -1)[0]
    if verbose:
        bb = np.append([1.0], -b)
        roots = np.roots(bb)
        is_unit = np.less(np.abs(roots), 1.0)
        print(f"is unit root = {np.all(is_unit)}")
    b = pd.Series(b, index=x.columns)
    return b


def rolling_estimate_ar_p_process_with_lasso(y: pd.Series,
                                             lasso_model: LassoModel,
                                             num_of_lags: int = 2,
                                             verbose: bool = True
                                             ) -> pd.DataFrame:

    bs = {}
    for idx, date in enumerate(y.index):
        if idx > lasso_model.warmup_period:  # global warm-up period
            bs[date] = estimate_ar_p_process_with_lasso(y=y.loc[:date],
                                                 lasso_model=lasso_model,
                                                 num_of_lags=num_of_lags,
                                                 verbose=verbose)
    bs = pd.DataFrame.from_dict(bs, orient='index')
    return bs


def adjust_returns_ar_p_process_with_lasso(y: pd.Series,
                                           lasso_model: LassoModel,
                                           num_of_lags: int = 2,
                                           verbose: bool = True
                                           ) -> pd.Series:
    b = rolling_estimate_ar_p_process_with_lasso(y=y, lasso_model=lasso_model, num_of_lags=num_of_lags, verbose=verbose)
    b = b.reindex(index=y.index).bfill()
    print(b)

    x = compute_lags_x(y=y, num_of_lags=num_of_lags)
    print(x)
    prediction = np.nansum(x * b, axis=1)
    unsmoothed = (y - prediction) / (1.0-np.nansum(b, axis=1))
    return unsmoothed


def produce_illiquidity_report(prices: pd.DataFrame,
                               benchmark_price: pd.Series,
                               span: int = 20,
                               mean_adj_type: qis.MeanAdjType = qis.MeanAdjType.NONE,
                               warmup_period: Optional[int] = 10
                               ) -> List[plt.Figure]:

    navs_unsmoothed, unsmoothed, ar_betas, ewm_r2 = compute_ar1_unsmoothed_prices(prices=prices,
                                                                                  freq='QE',
                                                                                  span=span,
                                                                                  mean_adj_type=mean_adj_type,
                                                                                  warmup_period=warmup_period)

    # estimate equity betas
    linear_model = qis.estimate_linear_model(asset_prices=prices, factor_prices=benchmark_price, freq='QE', span=12)
    equity_betas_reported = linear_model.get_factor1_loadings()
    linear_model = qis.estimate_linear_model(asset_prices=navs_unsmoothed, factor_prices=benchmark_price, freq='QE', span=12)
    equity_betas_smoothed = linear_model.get_factor1_loadings()


    figs = []
    kwargs = dict(framealpha=0.9)
    with sns.axes_style("darkgrid"):
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        qis.plot_time_series(df=ar_betas,
                             title='AR-1 betas',
                             ax=ax,
                             **kwargs)
        figs.append(fig)
        for asset in prices.columns:
            asset_navs = pd.concat([prices[asset].rename('reported'),
                                    navs_unsmoothed[asset].rename('unsmoothed')], axis=1)
            asset_betas = pd.concat([equity_betas_reported[asset].rename('reported'),
                                    equity_betas_smoothed[asset].rename('unsmoothed')], axis=1)

            fig, axs = plt.subplots(2, 2, figsize=(12, 8))
            figs.append(fig)
            qis.set_suptitle(fig, title=f"{asset}")

            qis.plot_prices_with_dd(prices=asset_navs,
                                    perf_params=qis.PerfParams(freq='QE'),
                                    axs=axs[:, 0],
                                    **kwargs)
            qis.plot_time_series(df=asset_betas,
                                 title='Equity Betas',
                                 ax=axs[0, 1],
                                 **kwargs)
            axs[0, 1].set_xticklabels('')
            qis.plot_time_series_2ax(df1=ar_betas[asset].rename('beta'),
                                     df2=ewm_r2[asset].rename('R^2'),
                                     legend_stats=qis.LegendStats.AVG_LAST,
                                     legend_stats2=qis.LegendStats.AVG_LAST,
                                     var_format='{:,.2f}',
                                     var_format_yax2='{:,.0%}',
                                     title='Ar1 Betas',
                                     ax=axs[1, 1],
                                     **kwargs)
    return figs


class UnitTests(Enum):
    ESTIMATE_AR = 1
    ROLLING_ESTIMATE = 2
    ADJUST_RETURNS = 3
    ROLLING_BETA = 4
    REPORT = 5


def run_unit_test(unit_test: UnitTests):

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
    # local_path_out = lp.get_output_path()

    lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                             group_data=None,
                             demean=False,
                             reg_lambda=1e-5,  # 2.5*1e-5
                             span=40,
                             solver='ECOS_BB',
                             warmup_period=12)

    is_funds_universe = True
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)

    time_period = qis.TimePeriod('31Dec1999', '31Mar2025')

    prices = universe_data.get_saa_prices(time_period=time_period)
    y = qis.to_returns(prices['Private Equity'], freq='QE', drop_first=True)

    if unit_test == UnitTests.ESTIMATE_AR:
        b = estimate_ar_p_process_with_lasso(y=y, lasso_model=lasso_model, num_of_lags=4)
        print(b)

    elif unit_test == UnitTests.ROLLING_ESTIMATE:
        b = rolling_estimate_ar_p_process_with_lasso(y=y, lasso_model=lasso_model, num_of_lags=1)
        print(b)

        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            qis.plot_time_series(df=b,
                                 title='AR betas at lags',
                                 ax=ax)

    elif unit_test == UnitTests.ADJUST_RETURNS:
        unsmoothed = adjust_returns_ar_p_process_with_lasso(y=y, lasso_model=lasso_model, num_of_lags=2)
        print(unsmoothed)
        df = pd.concat([y.rename('reported'), unsmoothed.rename('unsmoothed')], axis=1)
        navs = qis.returns_to_nav(returns=df)

        with sns.axes_style("darkgrid"):
            fig, axs = plt.subplots(2, 1, figsize=(8, 12))
        qis.plot_prices_with_dd(prices=navs, perf_params=qis.PerfParams(freq='QE'),
                                axs=axs)

    elif unit_test == UnitTests.ROLLING_BETA:
        unsmoothed, betas, ewm_r2 = adjust_returns_with_ar1(returns=y.to_frame(),
                                                            span=20,
                                                            mean_adj_type=qis.MeanAdjType.NONE,
                                                            warmup_period=10
                                                            )
        df = pd.concat([y.rename('reported'), unsmoothed.iloc[:, 0].rename('unsmoothed')], axis=1)
        navs = qis.returns_to_nav(returns=df)

        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            qis.plot_time_series(df=betas,
                                 title='AR-1 betas',
                                 ax=ax)

            fig, axs = plt.subplots(2, 1, figsize=(8, 12))
            qis.plot_prices_with_dd(prices=navs, perf_params=qis.PerfParams(freq='QE'),
                                    axs=axs)

    elif unit_test == UnitTests.REPORT:
        prices = universe_data.get_joint_prices()
        PE_ASSET_FOR_UNSMOOTHING = ['Private Equity', 'Private Debt', 'Insurance-Linked',
                                    'LGT Multi-Strategy (LMA)', 'Fermat CAT Bond Fund-F USD',
                                    'Hamilton Lane Global Private Assets Fund',
                                    'Franklin Lexington Private Markets Fund SICAV - Flex Feeder I USD',
                                    'PG3 Longreach Alternative Strategies Fund ',
                                    'Ares Strategic Income Offshore Access Fund USD',
                                    'Hamilton Lane Senior Credit Opportunities Fund I - USD'
                                    ]
        benchmark_price = prices['North America']
        prices = prices[PE_ASSET_FOR_UNSMOOTHING]
        figs = produce_illiquidity_report(prices=prices, benchmark_price=benchmark_price, span=20)
        qis.save_figs_to_pdf(figs, file_name='pe_unsmoothing', local_path=lp.get_output_path())

    plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.REPORT

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)
