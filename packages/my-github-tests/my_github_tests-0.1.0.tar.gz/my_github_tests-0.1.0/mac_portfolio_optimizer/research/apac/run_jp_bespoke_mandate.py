"""
run backtest for funds portfolio
"""
# packages
import pandas as pd
import qis as qis
from enum import Enum

from mac_portfolio_optimizer import (get_prod_covar_estimator, load_mac_portfolio_universe,
                                     AssetClasses,
                                     MacUniverseData,
                                     SaaPortfolio,
                                     SaaRangeConstraints,
                                     TaaPortfolio,
                                     backtest_saa_taa_portfolios,
                                     backtest_saa_risk_budget_portfolio,
                                     range_backtest_lasso_portfolio_with_alphas,
                                     generate_report)
from mac_portfolio_optimizer.research.apac.set_risk_budget_for_range_saa import solve_risk_budget_for_mandate


class LocalTests(Enum):
    SOLVE_SAA_RISK_BUDGET = 1
    RUN_MAC_BACKTEST = 2


class PflType(Enum):
    PFL1 = ('saa_index_PLF1', 'taa_PLF1')
    PFL2 = ('saa_index_PLF2', 'taa_PLF2')
    PFL3 = ('saa_index_PLF3', 'taa_PLF3')

@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    time_period = qis.TimePeriod('31Dec2004', '30Jun2025')

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    local_path_out = lp.get_output_path()

    # load universe
    pfl_type = PflType.PFL3
    universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                saa_portfolio=pfl_type.value[0],
                                                taa_portfolio=pfl_type.value[1],
                                                saa_range_constraints='saa_asset_class_PLF')

    # set lasso model params
    if local_test == LocalTests.SOLVE_SAA_RISK_BUDGET:
        saa_rebalancing_freq = 'YE'
        covar_estimator = get_prod_covar_estimator(rebalancing_freq=saa_rebalancing_freq)

        risk_budget, saa_rolling_weights, multi_portfolio_data = solve_risk_budget_for_mandate(universe_data=universe_data,
                                                                                               covar_estimator=covar_estimator,
                                                                                               time_period=time_period,
                                                                                               saa_rebalancing_freq=saa_rebalancing_freq)
        print(risk_budget)
        risk_budget.to_clipboard()
        report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                        reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                        add_rates_data=False)
        figs1 = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                              add_benchmarks_to_navs=True,
                                                              add_exposures_comp=False,
                                                              add_strategy_factsheet=True,
                                                              time_period=time_period,
                                                              **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name=f"{pfl_type.value}_risk_budgets", local_path=lp.get_output_path())

    elif local_test == LocalTests.RUN_MAC_BACKTEST:

        # set model params
        apply_unsmoothing_for_pe = True
        returns_freqs = universe_data.get_joint_rebalancing_freqs()
        covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                   apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                   returns_freqs=returns_freqs)

        group_max_turnover_constraint = pd.Series({0: 1.0,
                                                   1: 0.25,
                                                   2: 0.1,
                                                   3: 0.1,
                                                   4: 0.1,
                                                   5: 0.1})
        tracking_err_vol_constraint = 0.025
        group_tracking_err_vol_constraint = pd.Series({AssetClasses.FI.value: tracking_err_vol_constraint,
                                                       AssetClasses.EQ.value: tracking_err_vol_constraint,
                                                       AssetClasses.ALTS.value: tracking_err_vol_constraint})

        group_tracking_err_vol_constraint = pd.Series({AssetClasses.FI.value: 0.0075,
                                                       AssetClasses.EQ.value: 0.025,
                                                       AssetClasses.ALTS.value: 0.0325})
        group_tracking_err_vol_constraint = pd.Series({AssetClasses.FI.value: 0.01,
                                                       AssetClasses.EQ.value: 0.05,
                                                       AssetClasses.ALTS.value: 0.06})
        meta_params = dict(global_tracking_err_vol_constraint=None,
                           group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                           global_max_turnover_constraint=None,
                           group_max_turnover_constraint=group_max_turnover_constraint,
                           management_fee=0.00,
                           is_saa_benchmark_for_betas=True,
                           is_joint_saa_taa_covar=True,
                           rebalancing_costs=0.0,
                           saa_rebalancing_freq='QE',
                           apply_unsmoothing_for_pe=apply_unsmoothing_for_pe)

        multi_portfolio_data, manager_alphas, taa_covar_data = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                           time_period=time_period,
                                                                           covar_estimator=covar_estimator,
                                                                           **meta_params)
        generate_report(multi_portfolio_data=multi_portfolio_data,
                        manager_alphas=manager_alphas,
                        taa_covar_data=taa_covar_data,
                        universe_data=universe_data,
                        time_period=time_period,
                        file_name=f"{pfl_type.value[1]}_mac_backtest",
                        local_path=lp.get_output_path())


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.RUN_MAC_BACKTEST)
