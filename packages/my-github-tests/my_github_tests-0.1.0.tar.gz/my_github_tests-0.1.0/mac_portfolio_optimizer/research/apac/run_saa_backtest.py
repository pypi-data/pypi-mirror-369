"""
run backtest for funds portfolio
"""
# packages
import pandas as pd
import matplotlib.pyplot as plt
import qis as qis
from enum import Enum
from optimalportfolios import LassoModelType, LassoModel, CovarEstimator, CovarEstimatorType

# project
from mac_portfolio_optimizer import (load_mac_portfolio_universe,
                                     SaaPortfolio,
                                     backtest_saa_risk_budget_portfolio)


class LocalTests(Enum):
    SAA_PORTFOLIO = 1


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
    # time_period = qis.TimePeriod('31Dec2022', '23Dec2024')
    # time_period = qis.TimePeriod('30Jun2013', '30Jun2023')

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    local_path_out = lp.get_output_path()

    # load universe
    universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                saa_portfolio=SaaPortfolio.SAA_BALANCED_APAC,
                                                taa_portfolio=SaaPortfolio.SAA_BALANCED_APAC,
                                                saa_range_constraints='saa_asset_class_RgBalAPAC')
    rebalancing_costs = 0.0

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
                                     rebalancing_freq='ME', # taa rebalancing
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

    group_tracking_err_vol_constraint = universe_data.set_group_uniform_tracking_error_constraint(tracking_err_vol_constraint=0.03)
    saa_rebalancing_freq = 'YE'
    meta_params = dict(group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                       group_max_turnover_constraint=group_max_turnover_constraint,
                       global_max_turnover_constraint=None,
                       management_fee=0.0,
                       is_saa_benchmark_for_betas=True,
                       rebalancing_costs=rebalancing_costs,
                       saa_rebalancing_freq=saa_rebalancing_freq)

    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)
    report_kwargs = qis.update_kwargs(report_kwargs, dict(ytd_attribution_time_period=qis.TimePeriod('31Dec2023', '31Dec2024')))
    from qis import PerfStat
    perf_columns = [PerfStat.TOTAL_RETURN, PerfStat.PA_RETURN,
                    PerfStat.VOL, PerfStat.SHARPE_RF0, PerfStat.SHARPE_EXCESS,
                    PerfStat.MAX_DD, PerfStat.SKEWNESS,
                    PerfStat.ALPHA_AN, PerfStat.BETA, PerfStat.R2, PerfStat.ALPHA_PVALUE]
    report_kwargs = qis.update_kwargs(report_kwargs, dict(perf_columns=perf_columns,
                                                          perf_stats_labels=[PerfStat.PA_RETURN, PerfStat.VOL, PerfStat.SHARPE_RF0]))

    if local_test == LocalTests.SAA_PORTFOLIO:

        # 1. solve saa
        saa_rolling_weights, saa_portfolio_data = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                     time_period=time_period,
                                                                                     covar_estimator=covar_estimator,
                                                                                     **meta_params)
        qis.save_df_to_excel(saa_rolling_weights, file_name='apac_saa', local_path=local_path_out,
                             add_current_date = True)


        # 2. run static weight benchmark
        saa_static_weights = universe_data.get_benchmark_static_weights()
        static_saa_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices,
                                                          weights=saa_static_weights,
                                                          rebalancing_freq=saa_rebalancing_freq,
                                                          management_fee=0.0,
                                                          ticker='SAA-Static')

        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio_data, static_saa_portfolio_data],
            benchmark_prices=universe_data.benchmarks,
            covar_dict=saa_portfolio_data.covar_dict)

        group_data, group_order = universe_data.get_joint_sub_ac_group_data()
        [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]

        figs1 = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                              strategy_idx=0,
                                                              benchmark_idx=1,
                                                              add_benchmarks_to_navs=True,
                                                              add_exposures_comp=False,
                                                              add_strategy_factsheet=True,
                                                              time_period=time_period,
                                                              **report_kwargs)
        plt.close('all')
        # generate tre figures
        report_kwargs = qis.update_kwargs(report_kwargs, dict(framealpha=0.9))  #, x_date_freq='YE'
        ac_group_data, ac_group_order = universe_data.get_joint_ac_group_data()
        sub_ac_group_data, sub_ac_group_order = universe_data.get_joint_sub_ac_group_data()
        figs2, dfs = qis.weights_tracking_error_report_by_ac_subac(multi_portfolio_data=multi_portfolio_data,
                                                                   time_period=time_period,
                                                                   ac_group_data=ac_group_data,
                                                                   ac_group_order=ac_group_order,
                                                                   sub_ac_group_data=sub_ac_group_data,
                                                                   sub_ac_group_order=sub_ac_group_order,
                                                                   turnover_groups=universe_data.get_taa_turnover_groups().apply(lambda x: f"Turnover group {x}"),
                                                                   turnover_order=universe_data.get_joint_turnover_order(),
                                                                   tre_max_clip=None,
                                                                   add_titles=True,
                                                                   **report_kwargs)

        for k, fig in figs2.items():
            figs1.append(fig)
        qis.save_figs_to_pdf(figs1, file_name='apac_saa_balanced', local_path=lp.get_output_path())


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.SAA_PORTFOLIO)
