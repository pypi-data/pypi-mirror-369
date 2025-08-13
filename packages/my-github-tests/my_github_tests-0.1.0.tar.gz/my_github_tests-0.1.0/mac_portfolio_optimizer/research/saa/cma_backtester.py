# packages
import pandas as pd
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, Dict, List
from enum import Enum

# project
from optimalportfolios import (CovarEstimator, rolling_maximise_alpha_over_tre)

from mac_portfolio_optimizer import get_prod_covar_estimator, MacUniverseData
from mac_portfolio_optimizer.research.saa.saa_excel_loader import load_saa_mac_universe
from mac_portfolio_optimizer.research.saa.saa_universe import (Family, BaseCcy, RiskProfile, AltIntType,
                                                               CmaType, SAA_AC_LEVEL1)


def backtest_saa_cma(universe_data: MacUniverseData,
                     covar_dict: Dict[pd.Timestamp, pd.DataFrame] = None,
                     covar_estimator: CovarEstimator = None,
                     time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                     global_tracking_err_vol_constraint: Optional[float] = None,
                     group_tracking_err_vol_constraint: Optional[pd.Series] = None,
                     global_max_turnover_constraint: Optional[float] = None,
                     group_max_turnover_constraint: Optional[pd.Series] = None,
                     management_fee: float = 0.0,
                     rebalancing_costs: float = 0.0,
                     ticker: str = 'SAA Optimal with CMA',
                     **kwargs
                     ) -> Tuple[pd.DataFrame, qis.PortfolioData]:
    """
    apply maximization of portfolio cmas subject to tracking error
    """
    if covar_dict is None:
        saa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=universe_data.get_risk_factors(),
                                                            prices=universe_data.saa_prices,
                                                            time_period=time_period)
        covar_dict = saa_covar_data.y_covars

    # 2. set saa_static_weights as benchmark weights
    saa_static_weights = universe_data.get_benchmark_static_weights()
    saa_static_weights_t = {date: saa_static_weights for date in list(covar_dict.keys())}
    saa_rolling_weights = pd.DataFrame.from_dict(saa_static_weights_t, orient='index')

    # 3. set taa type constraint on ac allocation and min max
    saa_constraints = universe_data.get_taa_constraints(global_tracking_err_vol_constraint=global_tracking_err_vol_constraint,
                                                        group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                                                        global_max_turnover_constraint=global_max_turnover_constraint,
                                                        group_max_turnover_constraint=group_max_turnover_constraint)

    # reindex at covar frequency
    saa_rolling_weights = saa_rolling_weights.reindex(index=list(covar_dict.keys()), method='ffill').ffill()

    # use cmas as alpha
    alphas = universe_data.cmas[saa_rolling_weights.columns].reindex(index=saa_rolling_weights.index, method='ffill').fillna(0.0)

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
                                                      ticker=ticker)
    group_data, group_order = universe_data.get_joint_ac_group_data()
    taa_portfolio_data.group_data=group_data
    taa_portfolio_data.group_order = group_order
    return taa_rolling_weights, taa_portfolio_data


def backtest_efficient_frontier(local_path: str,
                                covar_estimator: CovarEstimator,
                                cma_types: List[CmaType] = (CmaType.LGT_CMAS, CmaType.HISTORICAL_10Y, CmaType.FIXED_SHARPE, ),
                                family: Family = Family.CLASSIC,
                                base_ccy: BaseCcy = BaseCcy.USD,
                                alt_inv_type: AltIntType = AltIntType.AI,
                                time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                benchmark_underweight_ratio: float = 0.0,
                                benchmark_overweight_ratio: float = 2.0,
                                **meta_params
                                ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, qis.MultiPortfolioData]]:

    risk_profiles = list([x for x in RiskProfile])

    # saa_cma
    saa_cma_portfolio_curves = {}

    # static benchmarks
    benchmark_datas = []
    for risk_profile in risk_profiles:
        universe_data = load_saa_mac_universe(local_path=local_path,
                                              family=family,
                                              base_ccy=base_ccy,
                                              risk_profile=risk_profile,
                                              alt_inv_type=alt_inv_type,
                                              benchmark_underweight_ratio=benchmark_underweight_ratio,
                                              benchmark_overweight_ratio=benchmark_overweight_ratio)
        saa_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices,
                                                          weights=universe_data.get_benchmark_static_weights(),
                                                          rebalancing_freq=covar_estimator.rebalancing_freq,
                                                          ticker=risk_profile.value)
        saa_portfolio_data.group_data, saa_portfolio_data.group_order = universe_data.get_joint_ac_group_data()
        benchmark_datas.append(saa_portfolio_data)

    # benchmark_datas does not depend on cma so we use the last one
    saa_cma_portfolio_curves[f"SAA Static Benchmarks"] = qis.MultiPortfolioData(portfolio_datas=benchmark_datas,
                                                                                benchmark_prices=universe_data.benchmarks)
    # with cmas
    for cma_type in cma_types:
        saa_cma_portfolio_datas = []
        for risk_profile in risk_profiles:
            universe_data = load_saa_mac_universe(local_path=local_path,
                                                  family=family,
                                                  base_ccy=base_ccy,
                                                  risk_profile=risk_profile,
                                                  alt_inv_type=alt_inv_type,
                                                  cma_type=cma_type,
                                                  benchmark_underweight_ratio=benchmark_underweight_ratio,
                                                  benchmark_overweight_ratio=benchmark_overweight_ratio)

            taa_rolling_weights, taa_portfolio_data = backtest_saa_cma(universe_data=universe_data,
                                                                       time_period=time_period,
                                                                       covar_estimator=covar_estimator,
                                                                       ticker=risk_profile.value,
                                                                       **meta_params)
            saa_cma_portfolio_datas.append(taa_portfolio_data)

        curve_key = f"Optimal SAA with {cma_type.value}"
        saa_cma_portfolio_curves[curve_key] = qis.MultiPortfolioData(portfolio_datas=saa_cma_portfolio_datas,
                                                                     benchmark_prices=universe_data.benchmarks)

    portfolio_curves_navs = {}
    for key, portfolio_curve in saa_cma_portfolio_curves.items():
        portfolio_curves_navs[key] = portfolio_curve.get_navs(time_period=time_period)

    return portfolio_curves_navs, saa_cma_portfolio_curves


def plot_efficient_frontier(local_path: str,
                            time_period: qis.TimePeriod,
                            covar_estimator: CovarEstimator,
                            family: Family = Family.CLASSIC,
                            base_ccy: BaseCcy = BaseCcy.USD,
                            alt_inv_type: AltIntType = AltIntType.EX,
                            cma_types: List[CmaType] = (CmaType.LGT_CMAS, CmaType.HISTORICAL_10Y, CmaType.FIXED_SHARPE, ),
                            **kwargs):

    portfolio_curves_navs, portfolio_curves = backtest_efficient_frontier(local_path=local_path,
                                                                          time_period=time_period,
                                                                          covar_estimator=covar_estimator,
                                                                          family=family,
                                                                          base_ccy=base_ccy,
                                                                          alt_inv_type=alt_inv_type,
                                                                          cma_types=cma_types,
                                                                          **kwargs)
    colors = qis.get_n_colors(n=len(portfolio_curves_navs.keys()))
    markers = qis.get_n_markers(n=len(portfolio_curves_navs.keys()))
    title = f"base_ccy={base_ccy.value}, alt_inv_type={alt_inv_type.value}, tracking error=1.00%"
    with sns.axes_style("darkgrid"):
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        for idx, (key, navs) in enumerate(portfolio_curves_navs.items()):
            annotation_labels = navs.columns.to_list()
            qis.plot_ra_perf_scatter(prices=navs,
                                     perf_params=qis.PerfParams(freq='ME'),
                                     x_var=qis.PerfStat.VOL,
                                     y_var=qis.PerfStat.PA_RETURN,
                                     full_sample_color=colors[idx],
                                     order=1,
                                     add_universe_model_label=True,
                                     annotation_labels=annotation_labels,
                                     markers=[markers[idx]],
                                     annotation_marker=markers[idx],
                                     annotation_colors=[colors[idx]]*len(navs.columns),
                                     ci=None,
                                     ax=ax)
        qis.set_title(ax=ax, title=title)
        qis.set_legend(ax=ax, labels=list(portfolio_curves_navs.keys()),
                       markers=markers,
                       colors=colors)

    # weights
    weights_by_curve = {}
    for curve, portfolio_curve in portfolio_curves.items():
        # these are weights by cma type and dict{ac: mandate}
        weights_by_curve[curve] = portfolio_curve.get_grouped_weights(is_input_weights=False, freq='YE',
                                                                      time_period=time_period)
    # need to transform by ac type and dict{mandate: curve}
    acs = SAA_AC_LEVEL1
    acs_weights = { ac: {} for ac in acs}
    for ac in acs:
        for mandate in list(RiskProfile):
            dfs = []
            for curve, weights in weights_by_curve.items():
                if ac in weights.keys():  # need to fill in missing curves and acs
                    curve_mandate_ac_weight = weights[ac]
                    if mandate.value in curve_mandate_ac_weight.columns:
                        df = curve_mandate_ac_weight[mandate.value].rename(curve)
                    else:
                        df = pd.Series(name=curve)
                else:
                    df = pd.Series(name=curve)
                dfs.append(df)
            if len(dfs) > 0:
                acs_weights[ac][mandate.value] = pd.concat(dfs, axis=1)

    avg_weights = {}
    for ac, dfs in acs_weights.items():
        weights_by_mandate = {}
        for mandate, df in dfs.items():
            weights_by_mandate[mandate] = df.mean(0)
        avg_weights[ac] = pd.DataFrame.from_dict(weights_by_mandate, orient='index')

    with sns.axes_style("darkgrid"):
        fig, axs = plt.subplots(1, len(avg_weights.keys()), figsize=(16, 8))
        qis.set_suptitle(fig=fig, title=title)

        for idx, (ac, df) in enumerate(avg_weights.items()):
            qis.plot_bars(df=df,
                          stacked=False,
                          yvar_format='{:,.0%}',
                          title=ac,
                          ax=axs[idx])

        """
        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            qis.df_dict_boxplot_by_columns(dfs=dfs,
                                           hue_var_name='assets',
                                           y_var_name='weights',
                                           ylabel='weights',
                                           legend_loc='upper center',
                                           title=key,
                                           ncols=2,
                                           ax=ax)
        """


class LocalTests(Enum):
    BACKTEST_SAA_CMA = 1
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

    rebalancing_costs = 0.00

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

    covar_estimator = get_prod_covar_estimator(rebalancing_freq='YE')

    if local_test == LocalTests.BACKTEST_SAA_CMA:
        universe_data = load_saa_mac_universe(local_path=local_path,
                                              family=Family.CLASSIC,
                                              base_ccy=BaseCcy.USD,
                                              risk_profile=RiskProfile.MODERATE,
                                              alt_inv_type=AltIntType.AI,
                                              cma_type=CmaType.LGT_CMAS)

        weights, portfolio_data = backtest_saa_cma(universe_data=universe_data,
                                                   covar_estimator=covar_estimator,
                                                   time_period=time_period,
                                                   ticker='SAA Optimal with CMA',
                                                   **meta_params)

        figs = qis.generate_strategy_factsheet(portfolio_data=portfolio_data,
                                               benchmark_prices=universe_data.benchmarks,
                                               time_period=time_period,
                                               **qis.fetch_default_report_kwargs(time_period=time_period))
        plt.close('all')
        qis.save_figs_to_pdf(figs, file_name='saa_cma_porfolio', local_path=lp.get_output_path())

    elif local_test == LocalTests.PRODUCE_EFFICIENT_FRONTIER:

        cma_types = [CmaType.LGT_CMAS, CmaType.US_NO_VALUATION]
        # cma_types = [CmaType.LGT_CMAS, CmaType.AQR, CmaType.HISTORICAL_10Y, CmaType.FIXED_SHARPE]
        cma_types = [CmaType.LGT_CMAS, CmaType.AQR, CmaType.HISTORICAL_10Y]
        # cma_types = [CmaType.LGT_CMAS, CmaType.HISTORICAL_10Y, CmaType.FIXED_SHARPE]
        # cma_types = [CmaType.LGT_CMAS]

        plot_efficient_frontier(local_path=local_path,
                                time_period=time_period,
                                covar_estimator=covar_estimator,
                                cma_types=cma_types,
                                family=Family.CLASSIC,
                                base_ccy=BaseCcy.EUR,
                                alt_inv_type=AltIntType.AI,
                                **meta_params)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.PRODUCE_EFFICIENT_FRONTIER)
