"""
analytics for computing funds alpha using Group Lasso model
"""

import pandas as pd
import qis as qis
import matplotlib.pyplot as plt
from enum import Enum

from optimalportfolios import LassoModelType, LassoModel, estimate_lasso_regression_alphas


class LocalTests(Enum):
    CTA_ALPHA = 1
    HF_ALPHA = 2


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
    from mac_portfolio_optimizer.old_data.index_universe import load_index_universe_data

    universe_data = load_index_universe_data(local_path=local_path)
    benchmark_prices = universe_data.risk_factors_prices
    time_period = qis.TimePeriod('31Dec2014', '18Dec2024')
    benchmark_prices = time_period.locate(benchmark_prices)

    if local_test == LocalTests.CTA_ALPHA:

        ctas = qis.load_df_from_csv(file_name='ctas_bbg', local_path=lp.get_resource_path())
        prices = time_period.locate(ctas)
        lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO,
                                 group_data=pd.Series('CTA', index=ctas.columns),
                                 demean=True,
                                 reg_lambda=1e-4,
                                 span=12,
                                 solver='ECOS_BB')

        excess_returns = estimate_lasso_regression_alphas(prices=prices,
                                                          risk_factors_prices=benchmark_prices,
                                                          lasso_model=lasso_model,
                                                          rebalancing_freq='QE')

    elif local_test == LocalTests.HF_ALPHA:
        gf_group = universe_data.group_data_sub_ac
        gf_group = gf_group.index[gf_group == 'Hedge Funds'].to_list()
        hfs = universe_data.taa_prices[gf_group]
        prices = time_period.locate(hfs)
        lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO,
                                 group_data=pd.Series('HFs', index=prices.columns),
                                 demean=True,
                                 reg_lambda=1e-5,
                                 span=12,
                                 solver='ECOS_BB')
        excess_returns = estimate_lasso_regression_alphas(prices=prices,
                                                          risk_factors_prices=benchmark_prices,
                                                          lasso_model=lasso_model,
                                                          rebalancing_freq='QE')
        print(excess_returns.cumsum(0))

    qis.plot_time_series(excess_returns.cumsum(0))

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.CTA_ALPHA)

