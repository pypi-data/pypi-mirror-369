"""
run backtest for funds portfolio
"""
# packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import qis as qis
from enum import Enum

from mac_portfolio_optimizer import (get_prod_covar_estimator,
                                     load_mac_portfolio_universe,
                                     SaaPortfolio,
                                     RiskModel,
                                     TaaPortfolio,
                                     backtest_saa_taa_portfolios,
                                     backtest_saa_risk_budget_portfolio,
                                     range_backtest_lasso_portfolio_with_alphas,
                                     generate_report)


class LocalTests(Enum):
    SAA_PORTFOLIO = 1
    SAA_TAA_BACKTEST_REPORT = 2
    SAA_TAA_BACKTEST_RANGE = 3


@qis.timer
def run_local_test(local_test: LocalTests):
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')
    # time_period = qis.TimePeriod('31Dec2022', '23Dec2024')
    # time_period = qis.TimePeriod('30Jun2013', '30Jun2023')

    import mac_portfolio_optimizer.local_path as lp
    local_path = f"{lp.get_resource_path()}"
    # local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
    local_path_out = lp.get_output_path()

    # load universe
    is_funds_universe = False
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        file_name = 'funds_saa_taa_portfolio'
        rebalancing_costs = 0.0
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        file_name = 'paper_saa_taa'
        rebalancing_costs = 0.0020

    # set lasso model params
    saa_rebalancing_freq = 'QE'
    apply_unsmoothing_for_pe = True
    returns_freqs = universe_data.get_joint_rebalancing_freqs()
    covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=returns_freqs)

    group_max_turnover_constraint = pd.Series({0: 1.0,
                                               1: 0.20,
                                               2: 0.10,
                                               3: 0.10})

    tracking_err_vol_constraint = 0.035  # in paper = 0.03
    group_tracking_err_vol_constraint = universe_data.set_group_uniform_tracking_error_constraint(
        tracking_err_vol_constraint=tracking_err_vol_constraint)
    meta_params = dict(group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                       group_max_turnover_constraint=group_max_turnover_constraint,
                       global_max_turnover_constraint=None,
                       management_fee=0.0,
                       is_saa_benchmark_for_betas=True,
                       rebalancing_costs=rebalancing_costs,
                       saa_rebalancing_freq=saa_rebalancing_freq)

    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=True)
    report_kwargs = qis.update_kwargs(report_kwargs, dict(ytd_attribution_time_period=qis.TimePeriod('31Dec2023', '31Dec2024')))
    from qis import PerfStat
    perf_columns = [PerfStat.TOTAL_RETURN, PerfStat.PA_RETURN,
                    PerfStat.VOL, PerfStat.SHARPE_RF0, PerfStat.SHARPE_EXCESS,
                    PerfStat.MAX_DD, PerfStat.SKEWNESS,
                    PerfStat.ALPHA_AN, PerfStat.BETA, PerfStat.R2, PerfStat.ALPHA_PVALUE]
    report_kwargs = qis.update_kwargs(report_kwargs, dict(perf_columns=perf_columns,
                                                          perf_stats_labels=[PerfStat.PA_RETURN, PerfStat.VOL, PerfStat.SHARPE_RF0]))

    if local_test == LocalTests.SAA_PORTFOLIO:
        this = universe_data.get_saa_risk_budget()
        saa_rolling_weights, saa_portfolio_data = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                     time_period=time_period,
                                                                                     covar_estimator=covar_estimator,
                                                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                                                     **meta_params)

        strategy_risk_contributions_subac = saa_portfolio_data.compute_risk_contributions_implied_by_covar(
            group_data=universe_data.get_saa_sub_asset_class_data(),
            group_order=universe_data.sub_ac_group_order, normalise=True)

        df1 = pd.concat([universe_data.get_saa_risk_budget().rename('Given Risk\nBudget'),
                         strategy_risk_contributions_subac.mean(0).rename('Avg Ex Post\nRisk Contributions'),
                         saa_rolling_weights.mean(0).rename('Avg Realised\nWeights')
                         ], axis=1)
        qis.plot_df_table(df=df1,
                          index_column_name='Sub-Asset Class',
                          fontsize=12,
                          var_format='{:.2%}',
                          title='Risk Budget')

        # risk budget with
        fig_rc_weights = plt.figure(figsize=(14, 8), constrained_layout=True)
        gs = fig_rc_weights.add_gridspec(nrows=2, ncols=1, wspace=0.0, hspace=0.0)
        # qis.set_suptitle(fig_rc_weights, title='Static portfolio with average endowment weight')
        kwargs = dict(ncols=1, framealpha=0.9, fontsize=12,
                      colors=qis.get_n_sns_colors(n=len(strategy_risk_contributions_subac.columns), palette='tab10'),
                      legend_loc='upper left')
        qis.plot_stack(df=strategy_risk_contributions_subac,
                       use_bar_plot=True,
                       legend_stats=qis.LegendStats.AVG_NONNAN_LAST,
                       var_format='{:.1%}',
                       title='(A) Ex Post Risk Contributions',
                       ax=fig_rc_weights.add_subplot(gs[0, 0]),
                       **kwargs)

        qis.plot_stack(df=saa_rolling_weights,
                       use_bar_plot=True,
                       legend_stats=qis.LegendStats.AVG_NONNAN_LAST,
                       var_format='{:.1%}',
                       title='(B) SAA Weights',
                       ax=fig_rc_weights.add_subplot(gs[1, 0]),
                       **kwargs)

        #qis.save_fig(fig_rc_weights, file_name='fig_rc_weights', local_path=local_path_out)
        dfs_out = dict(fig_rc_weights=df1, risk_contributions=strategy_risk_contributions_subac, weights=saa_rolling_weights)
        qis.save_df_to_excel(dfs_out, file_name='fig_rc_weights', local_path=local_path_out)
        plt.show()

    elif local_test == LocalTests.SAA_TAA_BACKTEST_REPORT:
        multi_portfolio_data, manager_alphas, taa_covar_data = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                           time_period=time_period,
                                                                           covar_estimator=covar_estimator,
                                                                           apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                                           **meta_params)
        # [x.set_group_data(group_data=group_data_short, group_order=group_order_short) for x in multi_portfolio_data.portfolio_datas]
        multi_portfolio_data.benchmark_prices = universe_data.compute_static_weight_saa_benchmark(management_fee=0.0).to_frame()

        generate_report(multi_portfolio_data=multi_portfolio_data,
                        manager_alphas=manager_alphas,
                        taa_covar_data=taa_covar_data,
                        universe_data=universe_data,
                        time_period=time_period,
                        file_name=f"{file_name}",
                        local_path=lp.get_output_path(),
                        save_figures_png=False)

        dates = ['31Dec2015', '31Dec2020', '31Dec2024']
        with sns.axes_style('darkgrid'):
            fig_alpha, axs = plt.subplots(1, len(dates), figsize=(14, 12), constrained_layout=True)
            for idx, date in enumerate(dates):
                current_alpha = manager_alphas.alpha_scores.loc[date, :].to_frame()
                qis.plot_vbars(df=current_alpha,
                               title=f"({qis.idx_to_alphabet(idx=idx+1)}) {date}",
                               legend_loc=None,
                               add_bar_values=False,
                               add_total_bar=False,
                               colors=['blue'],
                               var_format='{:.1f}',
                               x_limits=(-3.0, 3.0),
                               ax=axs[idx])
        qis.save_fig(fig=fig_alpha, file_name='fig_alpha', local_path=local_path_out)

    elif local_test == LocalTests.SAA_TAA_BACKTEST_RANGE:

        saa_multi_portfolio_data, taa_multi_portfolio_data = \
            range_backtest_lasso_portfolio_with_alphas(universe_data=universe_data,
                                                       time_period=time_period,
                                                       covar_estimator=covar_estimator,
                                                       **meta_params)
        saa_multi_portfolio_data.benchmark_prices = universe_data.compute_static_weight_saa_benchmark(management_fee=0.0).to_frame()
        taa_multi_portfolio_data.benchmark_prices = universe_data.compute_static_weight_saa_benchmark(management_fee=0.0).to_frame()

        saa_table = saa_multi_portfolio_data.plot_ra_perf_table(time_period=time_period, is_convert_to_str=False, **report_kwargs)
        taa_table = taa_multi_portfolio_data.plot_ra_perf_table(time_period=time_period, is_convert_to_str=False, **report_kwargs)
        qis.save_df_to_excel(data=dict(saa_table=saa_table, taa_table=taa_table), file_name='cross_ra_60', local_path=lp.get_output_path() )

        figs1 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=saa_multi_portfolio_data,
                                                       backtest_name='SAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name='paper_saa_lasso_portfolio_range', local_path=lp.get_output_path())

        figs2 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=taa_multi_portfolio_data,
                                                       backtest_name='TAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs2, file_name='paper_taa_lasso_portfolio_range', local_path=lp.get_output_path())


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.SAA_TAA_BACKTEST_REPORT)
