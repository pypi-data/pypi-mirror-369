"""
run backtest for funds portfolio
"""
# packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import qis as qis
from enum import Enum
from optimalportfolios import LassoModelType, LassoModel, CovarEstimator, CovarEstimatorType, Constraints

# project
from mac_portfolio_optimizer import load_mac_portfolio_universe, SaaPortfolio, TaaPortfolio, backtest_saa_risk_budget_portfolio
from mac_portfolio_optimizer.research.saa.saa_excel_loader import load_qach_prices, CMAS_FEEDER_EXCEL_FILE
from mac_portfolio_optimizer.research.saa.saa_universe import CmaType


def generate_historical_10y_returns(local_path: str,
                                    freq: str = 'QE',
                                    span: int = 4*10
                                    ) -> pd.DataFrame:
    """
    historical return based on last 10y of quarterly returns
    """
    prices = load_qach_prices(local_path=local_path)
    prices = prices.resample(freq).last()
    returns = qis.to_returns(prices, drop_first=True)
    long_term_returns = 4.0*qis.compute_ewm(data=returns, span=span)
    return long_term_returns


def generate_fixed_sharpe_ratio_returns(local_path: str,
                                        freq: str = 'QE',
                                        span: int = 4*5,
                                        fixed_sharpe: float = 0.3
                                        ) -> pd.DataFrame:
    """
    historical return based on last 5y of quarterly vols
    """
    prices = load_qach_prices(local_path=local_path)
    prices = prices.resample(freq).last()
    returns = qis.to_returns(prices, drop_first=True)
    vols = qis.compute_ewm_vol(data=returns, span=span, annualization_factor=4)
    long_term_returns = fixed_sharpe * vols
    return long_term_returns


def generate_mac_implied_returns(local_path: str):

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')

    # load universe
    is_funds_universe = True
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)
        file_name = 'funds_saa_taa_portfolio'
        rebalancing_costs = 0.0
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)
        file_name = 'paper_saa_taa'
        rebalancing_costs = 0.0020

    # set lasso model params
    lasso_group_data, _ = universe_data.get_joint_sub_ac_group_data()
    lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                             group_data=lasso_group_data,
                             demean=True,
                             reg_lambda=1e-5,  # 2.5*1e-5
                             span=36,
                             solver='ECOS_BB')

    # set covar estimator
    covar_estimator = CovarEstimator(covar_estimator_type=CovarEstimatorType.LASSO,
                                     lasso_model=lasso_model,
                                     factor_returns_freq='ME',
                                     rebalancing_freq='ME',  # taa rebalancing
                                     returns_freqs=universe_data.get_joint_rebalancing_freqs(),
                                     span=lasso_model.span,
                                     is_apply_vol_normalised_returns=False,
                                     squeeze_factor=0.0,
                                     residual_var_weight=1.0,
                                     span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                     num_lags_newey_west_dict={'ME': 0, 'QE': 2}
                                     )

    group_max_turnover_constraint = pd.Series({0: 1.0,
                                               1: 0.20,
                                               2: 0.10,
                                               3: 0.10})

    group_tracking_err_vol_constraint = universe_data.set_group_uniform_tracking_error_constraint(
        tracking_err_vol_constraint=0.03)
    meta_params = dict(group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                       group_max_turnover_constraint=group_max_turnover_constraint,
                       global_max_turnover_constraint=None,
                       management_fee=0.0,
                       is_saa_benchmark_for_betas=True,
                       rebalancing_costs=rebalancing_costs,
                       saa_rebalancing_freq='QE')

    saa_rolling_weights, saa_portfolio_data = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                 time_period=time_period,
                                                                                 covar_estimator=covar_estimator,
                                                                                 saa_constraints=Constraints(
                                                                                     is_long_only=True),
                                                                                 **meta_params)

    risk_aversion = 12.0
    covars = saa_portfolio_data.covar_dict
    returns = {}
    sharpes = {}
    for date, covar in covars.items():
        weights = saa_rolling_weights.loc[date, :]
        returns_t = risk_aversion * covar @ weights
        returns[date] = returns_t
        sharpes[date] = returns_t / np.sqrt(np.diag(covar))
    returns = pd.DataFrame.from_dict(returns, orient='index')
    print(returns)
    sharpes = pd.DataFrame.from_dict(sharpes, orient='index')
    print(sharpes)

    metrics = dict(returns=returns, Sharpe=sharpes)
    var_formats = ['{:,.2%}', '{:,.2f}']
    for midx, (metric, data) in enumerate(metrics.items()):
        group_data, ac_group_order = universe_data.get_joint_ac_group_data()
        dfs = qis.split_df_by_groups(df=data, group_data=group_data, group_order=ac_group_order)

        kwargs = dict(fontsize=10, framealpha=0.9)
        with sns.axes_style('darkgrid'):
            fig, axs = plt.subplots(len(dfs.keys()), 1, figsize=(16, 12), tight_layout=True)
            for idx, (key, df) in enumerate(dfs.items()):
                qis.plot_time_series(df=df,
                                     title=f"{key}-{metric}",
                                     var_format=var_formats[midx],
                                     ax=axs[idx],
                                     **kwargs)


class LocalTests(Enum):
    HISTORICAL_RETURNS = 1
    FIXED_SHARPE = 2
    MAC_IMPLIED_RETURNS = 3


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    # local_path_out = lp.get_output_path()

    if local_test == LocalTests.HISTORICAL_RETURNS:
        long_term_returns = generate_historical_10y_returns(local_path=local_path)
        print(long_term_returns)
        qis.save_df_to_excel(data=long_term_returns, file_name=CMAS_FEEDER_EXCEL_FILE, local_path=local_path,
                             sheet_names=CmaType.HISTORICAL_10Y.value, mode='a')

    elif local_test == LocalTests.FIXED_SHARPE:
        long_term_returns = generate_fixed_sharpe_ratio_returns(local_path=local_path)
        print(long_term_returns)
        qis.save_df_to_excel(data=long_term_returns, file_name=CMAS_FEEDER_EXCEL_FILE, local_path=local_path,
                             sheet_names=CmaType.FIXED_SHARPE.value, mode='a')

    elif local_test == LocalTests.MAC_IMPLIED_RETURNS:
        generate_mac_implied_returns(local_path=local_path)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.HISTORICAL_RETURNS)
