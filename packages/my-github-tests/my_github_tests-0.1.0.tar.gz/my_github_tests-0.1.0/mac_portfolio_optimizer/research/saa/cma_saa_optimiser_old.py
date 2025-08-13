# packages
import pandas as pd
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Dict
from enum import Enum

# project
from optimalportfolios import (LassoModelType, LassoModel, CovarEstimator, CovarEstimatorType,
                               rolling_maximise_alpha_over_tre, rolling_risk_budgeting)

from optimalportfolios import solve_for_risk_budgets_from_given_weights

from mac_portfolio_optimizer.data.mac_universe import MacUniverseData, UniverseColumns
from mac_portfolio_optimizer.core.backtester_optimiser import backtest_saa_risk_budget_portfolio
from mac_portfolio_optimizer.research.saa.saa_excel_loader import load_saa_mac_universe
from mac_portfolio_optimizer.research.saa.saa_universe import (Family, BaseCcy, RiskProfile, AltIntType, CmaType)


def backtest_saa_cma_vs_risk_budget_vs_static(universe_data: MacUniverseData,
                                              covar_estimator: CovarEstimator,
                                              instrument_cma: pd.DataFrame,
                                              time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                              saa_rebalancing_freq: str = 'YE',
                                              global_tracking_err_vol_constraint: Optional[float] = None,
                                              group_tracking_err_vol_constraint: Optional[pd.Series] = None,
                                              global_max_turnover_constraint: Optional[float] = None,
                                              group_max_turnover_constraint: Optional[pd.Series] = None,
                                              management_fee: float = 0.0,
                                              rebalancing_costs: float = 0.0
                                              ) -> qis.MultiPortfolioData:

    # 1. estimate covar
    covar_estimator.rebalancing_freq = saa_rebalancing_freq
    taa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=universe_data.get_risk_factors(),
                                                        prices=universe_data.saa_prices,
                                                        time_period=time_period)
    covar_dict = taa_covar_data.y_covars


    # 2. run saa with static weights
    saa_static_weights = universe_data.get_benchmark_static_weights()
    saa_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices,
                                                weights=saa_static_weights,
                                                rebalancing_freq=saa_rebalancing_freq,
                                                management_fee=management_fee,
                                                ticker='SAA-Static')

    saa_static_weights_t = {date: saa_static_weights for date in list(covar_dict.keys())}
    saa_rolling_weights = pd.DataFrame.from_dict(saa_static_weights_t, orient='index')

    # 4. run tre portfolio
    saa_constraints = universe_data.get_taa_constraints(global_tracking_err_vol_constraint=global_tracking_err_vol_constraint,
                                                        group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                                                        global_max_turnover_constraint=global_max_turnover_constraint,
                                                        group_max_turnover_constraint=group_max_turnover_constraint)
    # saa_constraints = universe_data.get_saa_constraints(add_max_ac_constraints=True)
    print(saa_constraints)

    # reindex at covar frequency
    saa_rolling_weights = saa_rolling_weights.reindex(index=list(covar_dict.keys()), method='ffill').ffill()

    # use cmas as alpha
    alphas = instrument_cma[saa_rolling_weights.columns].reindex(index=saa_rolling_weights.index, method='ffill').fillna(0.0)

    taa_rolling_weights = rolling_maximise_alpha_over_tre(prices=universe_data.saa_prices,
                                                          alphas=alphas,
                                                          constraints0=saa_constraints,
                                                          benchmark_weights=saa_rolling_weights,
                                                          covar_dict=covar_dict,
                                                          time_period=time_period,
                                                          rebalancing_indicators=None,
                                                          apply_total_to_good_ratio=False)

    # taa portfolio
    taa_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices,
                                                      weights=taa_rolling_weights,
                                                      management_fee=management_fee,
                                                      rebalancing_costs=rebalancing_costs,
                                                      ticker='SAA-CMA')

    # risk-budget portfolio
    risk_budgets = solve_for_risk_budgets_from_given_weights(prices=universe_data.saa_prices,
                                                             given_weights=saa_static_weights,
                                                             time_period=time_period,
                                                             covar_dict=covar_dict)
    risk_budgets_weights = rolling_risk_budgeting(prices=universe_data.saa_prices,
                                                  time_period=time_period,
                                                  covar_dict=covar_dict,
                                                  risk_budget=risk_budgets,
                                                  constraints0=universe_data.get_saa_constraints(add_max_ac_constraints=True))

    risk_budget_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices,
                                                              weights=risk_budgets_weights,
                                                              management_fee=management_fee,
                                                              rebalancing_costs=rebalancing_costs,
                                                              ticker='SAA-RiskBudget')

    # multiportfolio including benchmark
    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[taa_portfolio_data,
                                                                   risk_budget_portfolio_data,
                                                                   saa_portfolio_data
                                                                   ],
                                                  benchmark_prices=universe_data.benchmarks,
                                                  covar_dict=covar_dict)
    group_data, group_order = universe_data.get_joint_sub_ac_group_data()
    [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]
    return multi_portfolio_data


def backtest_efficient_frontier(local_path: str,
                               covar_estimator: CovarEstimator,
                               time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                               **meta_params
                               ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, qis.MultiPortfolioData]]:

    risk_profiles = list([x for x in RiskProfile])
    cma_types = [CmaType.LGT_CMAS, CmaType.US_NO_VALUATION]
    navs_for_cma_types = []
    saa_cma_portfolio_curves = {}
    risk_budget_portfolios = {}

    for cma_type in cma_types:
        saa_cma_portfolio_datas = []
        risk_budget_portfolio_datas = []
        benchmark_datas = [] # benchmark_datas does not depend on cma so we use the last one
        for risk_profile in risk_profiles:
            universe_data = load_saa_mac_universe(local_path=local_path,
                                                  family=Family.CLASSIC,
                                                  base_ccy=BaseCcy.USD,
                                                  risk_profile=risk_profile,
                                                  alt_inv_type=AltIntType.AI,
                                                  cma_type=cma_type)
            instrument_cma = universe_data.cmas

            multi_portfolio_data = backtest_saa_cma_vs_risk_budget_vs_static(universe_data=universe_data,
                                                              time_period=time_period,
                                                              covar_estimator=covar_estimator,
                                                              instrument_cma=instrument_cma,
                                                              **meta_params)
            taa_portfolio_data = multi_portfolio_data.portfolio_datas[0]
            taa_portfolio_data.set_ticker(ticker=risk_profile.value)
            saa_cma_portfolio_datas.append(taa_portfolio_data)

            rb_portfolio_data = multi_portfolio_data.portfolio_datas[1]
            rb_portfolio_data.set_ticker(ticker=f"{risk_profile.value} - RiskBudget")
            risk_budget_portfolio_datas.append(rb_portfolio_data)

            benchmark_portfolio_data = multi_portfolio_data.portfolio_datas[2]
            benchmark_portfolio_data.set_ticker(ticker=risk_profile.value)
            benchmark_datas.append(benchmark_portfolio_data)


        curve_key = f"Optimal SAA with {cma_type.value}"
        saa_cma_portfolio_curves[curve_key] = qis.MultiPortfolioData(portfolio_datas=saa_cma_portfolio_datas,
                                                             benchmark_prices=universe_data.benchmarks)

        curve_key = f"RiskBudget"
        risk_budget_portfolios = qis.MultiPortfolioData(portfolio_datas=risk_budget_portfolio_datas,
                                                             benchmark_prices=universe_data.benchmarks)


    # benchmark_datas does not depend on cma so we use the last one
    saa_cma_portfolio_curves[f"RiskBudget"] = risk_budget_portfolios
    saa_cma_portfolio_curves[f"SAA Static Benchmarks"] = qis.MultiPortfolioData(portfolio_datas=benchmark_datas, benchmark_prices=universe_data.benchmarks)

    portfolio_curves_navs = {}
    for key, portfolio_curve in saa_cma_portfolio_curves.items():
        portfolio_curves_navs[key] = portfolio_curve.get_navs(time_period=time_period)

    return portfolio_curves_navs, saa_cma_portfolio_curves


class LocalTests(Enum):
    RUN_SAA_CMA_TO_STATIC = 1
    SOLVE_RISK_BUDGETS = 2
    PRODUCE_EFFICIENT_FRONTIER = 3


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
    local_path_out = lp.get_output_path()

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')
    # time_period = qis.TimePeriod('31Dec2023', '31Mar2025')

    rebalancing_costs = 0.0020

    lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                             group_data=None,
                             demean=True,
                             reg_lambda=1e-5,  # 2.5*1e-5
                             span=36,
                             solver='ECOS_BB')

    # set covar estimator
    covar_estimator = CovarEstimator(covar_estimator_type=CovarEstimatorType.LASSO,
                                     lasso_model=lasso_model,
                                     factor_returns_freq='ME',
                                     rebalancing_freq='YE',  # taa rebalancing
                                     returns_freqs='ME',
                                     span=lasso_model.span,
                                     is_apply_vol_normalised_returns=False,
                                     squeeze_factor=0.0,
                                     residual_var_weight=1.0,
                                     span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                     num_lags_newey_west_dict={'ME': 0, 'QE': 2}
                                     )

    meta_params = dict(global_tracking_err_vol_constraint=0.01,
                       group_tracking_err_vol_constraint=None,
                       global_max_turnover_constraint=0.5,
                       group_max_turnover_constraint=None,
                       management_fee=0.00,
                       rebalancing_costs=rebalancing_costs,
                       saa_rebalancing_freq='YE')

    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)
    report_kwargs = qis.update_kwargs(report_kwargs,
                                      dict(ytd_attribution_time_period=qis.TimePeriod('31Mar2024', '31Mar2025')))

    if local_test == LocalTests.RUN_SAA_CMA_TO_STATIC:

        universe_data = load_saa_mac_universe(local_path=local_path,
                                              family=Family.CLASSIC,
                                              base_ccy=BaseCcy.USD,
                                              risk_profile=RiskProfile.MODERATE,
                                              alt_inv_type=AltIntType.AI,
                                              cma_type=CmaType.US_NO_VALUATION)
        instrument_cma = universe_data.cmas

        multi_portfolio_data = backtest_saa_cma_vs_risk_budget_vs_static(universe_data=universe_data,
                                                          time_period=time_period,
                                                          covar_estimator=covar_estimator,
                                                          instrument_cma=instrument_cma,
                                                          **meta_params)
        figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                      add_benchmarks_to_navs=True,
                                                      time_period=time_period,
                                                      **report_kwargs)
        plt.close('all')
        qis.save_figs_to_pdf(figs, file_name='taa_cma_porfolio', local_path=lp.get_output_path())

    elif local_test == LocalTests.SOLVE_RISK_BUDGETS:
        universe_data = load_saa_mac_universe(local_path=local_path,
                                              family=Family.CLASSIC,
                                              base_ccy=BaseCcy.USD,
                                              risk_profile=RiskProfile.MODERATE,
                                              alt_inv_type=AltIntType.AI,
                                              cma_type=CmaType.US_NO_VALUATION)
        given_weights = universe_data.get_benchmark_static_weights()
        print(given_weights)

    elif local_test == LocalTests.PRODUCE_EFFICIENT_FRONTIER:
        portfolio_curves_navs, portfolio_curves = backtest_efficient_frontier(local_path=local_path,
                                                           time_period=time_period,
                                                           covar_estimator=covar_estimator,
                                                           **meta_params)
        """
        figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=portfolio_datas,
                                                      backtest_name="Efficient Frontier Backtest",
                                                      add_benchmarks_to_navs=True,
                                                      time_period=time_period,
                                                      **report_kwargs)

        plt.close('all')
        qis.save_figs_to_pdf(figs, file_name='cma_efficient_frontier_backtest', local_path=lp.get_output_path())
        """
        colors = qis.get_n_colors(n=len(portfolio_curves_navs.keys()))
        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            for idx, (key, navs) in enumerate(portfolio_curves_navs.items()):
                if idx == len(portfolio_curves_navs.keys())-1:
                    annotation_labels = navs.columns.to_list()
                else:
                    annotation_labels = None
                qis.plot_ra_perf_scatter(prices=navs,
                                         perf_params=qis.PerfParams(freq='ME'),
                                         x_var=qis.PerfStat.VOL,
                                         y_var=qis.PerfStat.PA_RETURN,
                                         full_sample_color=colors[idx],
                                         order=1,
                                         add_universe_model_label=True,
                                         annotation_labels=annotation_labels,
                                         title='Tracking error max = 1.00%',
                                         ax=ax)
            qis.set_legend(ax=ax, labels=list(portfolio_curves.keys()),
                           colors=colors)

            for idx, line in enumerate(ax.get_lines()):
                line.set_color(colors[idx])

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.PRODUCE_EFFICIENT_FRONTIER)
