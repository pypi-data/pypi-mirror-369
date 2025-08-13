"""
optimiser for the current portfolio
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import qis as qis
from enum import Enum
from optimalportfolios import LassoModelType, LassoModel, CovarEstimator, CovarEstimatorType

# project
from mac_portfolio_optimizer import (load_mac_portfolio_universe,
                                     SaaPortfolio,
                                     TaaPortfolio,
                                     run_current_saa_portfolio,
                                     run_current_saa_taa_portfolios,
                                     get_prod_covar_estimator,
                                     MacRangeConstraints,
                                     RiskModel)


class LocalTests(Enum):
    CURRENT_SAA_PORTFOLIO = 1
    CURRENT_SAA_TAA_PORTFOLIOS = 2


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # time_period = qis.TimePeriod('31Dec2004', '31Mar2025')
    time_period = qis.TimePeriod('31Dec2004', '31Jul2025')
    saa_valuation_date = pd.Timestamp('30Jun2025')
    taa_valuation_date = pd.Timestamp('31Jul2025')

    import mac_portfolio_optimizer.local_path as lp
    local_path = lp.get_resource_path()

    # load universe
    is_funds_universe = False
    mac_constraints = MacRangeConstraints.TYPE1.value
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                    sub_asset_class_ranges_sheet_name=mac_constraints,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        file_name = 'current_mac_unconstraint' if mac_constraints is None else  f"current_mac_{mac_constraints}"
        taa_weights_0 = universe_data.get_taa_current_weights()
        use_current_min_max = True
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS
                                                    )
        file_name = 'current_index_saa_taa_portfolio'
        taa_weights_0 = None
        use_current_min_max = False

    # set model params
    apply_unsmoothing_for_pe = True
    covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=universe_data.get_joint_rebalancing_freqs())
    returns_freqs = universe_data.get_joint_rebalancing_freqs()
    taa_rebalancing_indicators = pd.Series(np.where(returns_freqs=='ME', 1, 1), index=returns_freqs.index)
    print(taa_rebalancing_indicators)

    group_max_turnover_constraint = pd.Series({0: 1.0, 1: 0.25, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1})
    meta_params = dict(group_tracking_err_vol_constraint=universe_data.set_group_uniform_tracking_error_constraint(tracking_err_vol_constraint=0.025),
                       global_max_turnover_constraint=None,
                       group_max_turnover_constraint=group_max_turnover_constraint,
                       is_saa_benchmark_for_betas=True,
                       is_joint_saa_taa_covar=True)

    print("meta_params")
    print(meta_params)

    if local_test == LocalTests.CURRENT_SAA_PORTFOLIO:
        saa_portfolio = run_current_saa_portfolio(universe_data=universe_data,
                                                  saa_valuation_date=saa_valuation_date,
                                                  covar_estimator=covar_estimator,
                                                  **meta_params)
        print(saa_portfolio)

    elif local_test == LocalTests.CURRENT_SAA_TAA_PORTFOLIOS:
        saa_taa_portfolios = run_current_saa_taa_portfolios(universe_data=universe_data,
                                                            covar_estimator=covar_estimator,
                                                            saa_valuation_date=saa_valuation_date,
                                                            taa_valuation_date=taa_valuation_date,
                                                            time_period=time_period,
                                                            taa_weights_0=taa_weights_0,
                                                            taa_rebalancing_indicators=taa_rebalancing_indicators,
                                                            use_current_min_max=use_current_min_max,
                                                            **meta_params)
        qis.save_df_to_excel(data=saa_taa_portfolios.get_output_dict(),
                             file_name=file_name,
                             add_current_date=True, local_path=lp.get_output_path())
        # fig = saa_taa_portfolios.plot_taa_corr(fontsize=10)
        # qis.save_fig(fig, file_name='lasso_corr', local_path=lp.get_output_path())

        plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.CURRENT_SAA_TAA_PORTFOLIOS)
