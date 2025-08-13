"""
run backtest for funds portfolio
"""
# packages
import matplotlib.pyplot as plt
import pandas as pd
import qis as qis
from enum import Enum
from typing import List, Tuple, Dict, Any

# project
import mac_portfolio_optimizer.local_path as lp
from mac_portfolio_optimizer import (get_prod_covar_estimator,
                                     load_mac_portfolio_universe,
                                     MacUniverseData,
                                     SaaPortfolio,
                                     MacRangeConstraints,
                                     TaaPortfolio,
                                     backtest_saa_taa_portfolios,
                                     range_backtest_lasso_portfolio_with_alphas,
                                     tre_range_backtest_lasso_portfolio_with_alphas,
                                     RiskModel,
                                     generate_report,
                                     get_meta_params)


def run_mac_universe_vs_index_funds_backtest(local_path: str,
                                             time_period: qis.TimePeriod,
                                             meta_params: Dict,
                                             report_kwargs: Dict,
                                             apply_unsmoothing_for_pe: bool = True
                                             ) -> Tuple[List[plt.Figure], Dict[str, pd.DataFrame]]:
    # load universe
    funds_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                      saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                      taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)
    index_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                      saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                      taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)


    # funds
    funds_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                     returns_freqs=funds_universe_data.get_joint_rebalancing_freqs())
    funds_multi_portfolio_data, funds_manager_alphas, taa_covar_data = backtest_saa_taa_portfolios(universe_data=funds_universe_data,
                                                                                   time_period=time_period,
                                                                                   covar_estimator=funds_covar_estimator,
                                                                                   **meta_params)
    taa_funds_portfolio = funds_multi_portfolio_data.portfolio_datas[0].set_ticker('TAA Funds MAC')
    saa_portfolio = funds_multi_portfolio_data.portfolio_datas[1]

    # index
    index_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                     returns_freqs=index_universe_data.get_joint_rebalancing_freqs())
    index_multi_portfolio_data, index_manager_alphas, taa_covar_data = backtest_saa_taa_portfolios(universe_data=index_universe_data,
                                                                                   time_period=time_period,
                                                                                   covar_estimator=index_covar_estimator,
                                                                                   **meta_params)
    taa_index_portfolio = index_multi_portfolio_data.portfolio_datas[0].set_ticker('TAA Index MAC')

    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[taa_funds_portfolio, taa_index_portfolio, saa_portfolio],
                                                  benchmark_prices=funds_universe_data.benchmarks)

    figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                  backtest_name='SAA Funds & Index MAC Portfolios',
                                                  add_benchmarks_to_navs=True,
                                                  time_period=time_period,
                                                  **report_kwargs)

    # excel outputs
    navs = multi_portfolio_data.get_navs(add_benchmarks_to_navs=True, time_period=time_period)
    navs = navs.asfreq('ME', method='ffill').ffill()
    monthly_returns = qis.to_returns(prices=navs)
    perf_table = multi_portfolio_data.get_ra_perf_table(benchmark=funds_universe_data.benchmarks.columns[0],
                                                        time_period=time_period,
                                                        is_convert_to_str=False,
                                                        **report_kwargs)

    data = dict(perf_table=perf_table,
                navs=navs,
                monthly_returns=monthly_returns,
                taa_fund_weights=taa_funds_portfolio.get_input_weights()[funds_universe_data.taa_prices.columns],
                taa_index_weights=taa_index_portfolio.get_input_weights()[index_universe_data.taa_prices.columns],
                saa_weights=saa_portfolio.get_input_weights())

    return figs, data


def run_mac_pe_smoothed_vs_newey(universe_data: MacUniverseData,
                                 time_period: qis.TimePeriod,
                                 meta_params: Dict[str, Any]
                                 ) -> None:

    # PE unmoothing
    un_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                  apply_unsmoothing_for_pe=True,
                                                  returns_freqs=universe_data.get_joint_rebalancing_freqs())
    unmoothing_multi_portfolio_data, unmoothing_funds_manager_alphas, taa_covar_data = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                                                                   time_period=time_period,
                                                                                                                   covar_estimator=un_covar_estimator,
                                                                                                                   **meta_params)
    unmoothing_taa_portfolio = unmoothing_multi_portfolio_data.portfolio_datas[0].set_ticker('MAC with PE unmoothing')
    unmoothing_saa_portfolio = unmoothing_multi_portfolio_data.portfolio_datas[1].set_ticker('SAA with PE unmoothing')

    # Newey-West
    nw_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=False,
                                                     returns_freqs=universe_data.get_joint_rebalancing_freqs())
    nw_multi_portfolio_data, nw_manager_alphas, nw_covar_data = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                                            time_period=time_period,
                                                                                            covar_estimator=nw_covar_estimator,
                                                                                            **meta_params)
    nw_taa_portfolio = nw_multi_portfolio_data.portfolio_datas[0].set_ticker('MAC with Newey-West')
    nw_saa_portfolio = nw_multi_portfolio_data.portfolio_datas[1].set_ticker('SAA with Newey-West')

    saa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[unmoothing_saa_portfolio, nw_saa_portfolio],
                                                 benchmark_prices=universe_data.benchmarks,
                                                 covar_dict=unmoothing_multi_portfolio_data.covar_dict)

    taa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[unmoothing_taa_portfolio, nw_taa_portfolio],
                                                 benchmark_prices=universe_data.benchmarks,
                                                 covar_dict=unmoothing_multi_portfolio_data.covar_dict)

    generate_report(multi_portfolio_data=taa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=nw_covar_data,
                    universe_data=universe_data,
                    time_period=time_period,
                    file_name=f"mac_pe_unsmoothed_vs_nw",
                    save_excel=False,
                    local_path=lp.get_output_path())

    generate_report(multi_portfolio_data=saa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=nw_covar_data,
                    universe_data=universe_data,
                    time_period=time_period,
                    file_name=f"saa_pe_unsmoothed_vs_nw",
                    save_excel=False,
                    local_path=lp.get_output_path())


def run_risk_model_futures_vs_funds_backtest(local_path: str,
                                             time_period: qis.TimePeriod,
                                             meta_params: Dict,
                                             apply_unsmoothing_for_pe: bool = True,
                                             mac_constraints: str = MacRangeConstraints.UNCONSTRAINT.value
                                             ) -> None:
    # load universe
    universe_data1 = load_mac_portfolio_universe(local_path=local_path,
                                                 saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                 taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                 risk_model=RiskModel.FUTURES_RISK_FACTORS,
                                                 sub_asset_class_ranges_sheet_name=mac_constraints)
    universe_data2 = load_mac_portfolio_universe(local_path=local_path,
                                                 saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                 taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                 risk_model=RiskModel.PRICE_FACTORS_FROM_MAC_PAPER,
                                                 sub_asset_class_ranges_sheet_name=mac_constraints)

    funds_covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                                     apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                     returns_freqs=universe_data1.get_joint_rebalancing_freqs())

    # 1
    funds_multi_portfolio_data1, funds_manager_alphas1, taa_covar_data1 = backtest_saa_taa_portfolios(universe_data=universe_data1,
                                                                                   time_period=time_period,
                                                                                   covar_estimator=funds_covar_estimator,
                                                                                   **meta_params)
    taa_portfolio1 = funds_multi_portfolio_data1.portfolio_datas[0].set_ticker('MAC FuturesRisk')
    saa_portfolio1 = funds_multi_portfolio_data1.portfolio_datas[1].set_ticker('SAA FuturesRisk')

    # 2
    funds_multi_portfolio_data2, funds_manager_alphas2, taa_covar_data2 = backtest_saa_taa_portfolios(universe_data=universe_data2,
                                                                                   time_period=time_period,
                                                                                   covar_estimator=funds_covar_estimator,
                                                                                   **meta_params)
    taa_portfolio2 = funds_multi_portfolio_data2.portfolio_datas[0].set_ticker('MAC IndexRisk')
    saa_portfolio2 = funds_multi_portfolio_data2.portfolio_datas[1].set_ticker('SAA IndexRisk')

    saa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio1, saa_portfolio2],
                                                 benchmark_prices=universe_data1.benchmarks,
                                                 covar_dict=funds_multi_portfolio_data1.covar_dict)

    taa_portfolio_datas = qis.MultiPortfolioData(portfolio_datas=[taa_portfolio1, taa_portfolio2],
                                                 benchmark_prices=universe_data1.benchmarks,
                                                 covar_dict=funds_multi_portfolio_data1.covar_dict)

    generate_report(multi_portfolio_data=taa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=taa_covar_data1,
                    universe_data=universe_data1,
                    time_period=time_period,
                    file_name=f"mac_risk_model",
                    save_excel=False,
                    local_path=lp.get_output_path())

    generate_report(multi_portfolio_data=saa_portfolio_datas,
                    manager_alphas=None,
                    taa_covar_data=taa_covar_data1,
                    universe_data=universe_data1,
                    time_period=time_period,
                    file_name=f"saa_risk_model",
                    save_excel=False,
                    local_path=lp.get_output_path())


class LocalTests(Enum):
    SAA_TAA_BACKTEST_REPORT = 1  # standard backtest report
    SAA_TAA_BACKTEST_RANGE = 2
    SAA_TAA_BACKTEST_TRE_RANGE = 3
    INDEX_FUNDS_BACKTEST = 4  # backtest mac taa funds vs paper taa indices
    PE_SMOOTHING_VS_NEWEY_WEST = 5
    RISK_MODEL_FUTURES_VS_FUNDS_BACKTEST = 6


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # time_period = qis.TimePeriod('31Dec2022', '23Dec2024')
    # time_period = qis.TimePeriod('31Dec2022', '28Feb2025')
    # time_period = qis.TimePeriod('31Dec2004', '31May2025')
    time_period = qis.TimePeriod('31Dec2004', '31Jul2025')

    local_path = f"{lp.get_resource_path()}"

    # load universe
    is_funds_universe = True
    mac_constraints = MacRangeConstraints.TYPE1.value
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                    sub_asset_class_ranges_sheet_name=mac_constraints,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        file_name = 'mac_unconstraint' if mac_constraints is None else  f"mac_{mac_constraints}"
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)
        file_name = 'index_saa_taa_portfolio'

    # set model params
    apply_unsmoothing_for_pe = True
    covar_estimator = get_prod_covar_estimator(rebalancing_freq='ME',
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=universe_data.get_joint_rebalancing_freqs())
    meta_params = get_meta_params()

    # set report kwargs
    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)
    report_kwargs = qis.update_kwargs(report_kwargs, dict(ytd_attribution_time_period=qis.TimePeriod('30Jun2024', '31Jul2025')))

    if local_test == LocalTests.SAA_TAA_BACKTEST_REPORT:
        multi_portfolio_data, manager_alphas, taa_covar_data = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                           time_period=time_period,
                                                                           covar_estimator=covar_estimator,
                                                                           **meta_params)
        generate_report(multi_portfolio_data=multi_portfolio_data,
                        manager_alphas=manager_alphas,
                        taa_covar_data=taa_covar_data,
                        universe_data=universe_data,
                        time_period=time_period,
                        file_name=f"{file_name}",
                        local_path=lp.get_output_path())

    elif local_test == LocalTests.SAA_TAA_BACKTEST_RANGE:
        saa_multi_portfolio_data, taa_multi_portfolio_data = \
            range_backtest_lasso_portfolio_with_alphas(universe_data=universe_data,
                                                       time_period=time_period,
                                                       covar_estimator=covar_estimator,
                                                       **meta_params)

        figs1 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=saa_multi_portfolio_data,
                                                       backtest_name='SAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name='saa_lasso_portfolio_range', local_path=lp.get_output_path())

        figs2 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=taa_multi_portfolio_data,
                                                       backtest_name='TAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs2, file_name='taa_lasso_portfolio_range', local_path=lp.get_output_path())

    elif local_test == LocalTests.SAA_TAA_BACKTEST_TRE_RANGE:
        saa_multi_portfolio_data, taa_multi_portfolio_data = \
            tre_range_backtest_lasso_portfolio_with_alphas(universe_data=universe_data,
                                                           time_period=time_period,
                                                           covar_estimator=covar_estimator,
                                                           **meta_params)
        figs1 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=saa_multi_portfolio_data,
                                                       backtest_name='SAA Portfolios',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name='saa_tre_portfolio_range', local_path=lp.get_output_path())

        figs2 = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=taa_multi_portfolio_data,
                                                       backtest_name='TAA Portfolios for tracking error and turnover ranges',
                                                       time_period=time_period,
                                                       **report_kwargs)
        qis.save_figs_to_pdf(figs2, file_name='taa_tre_portfolio_range', local_path=lp.get_output_path())

    elif local_test == LocalTests.INDEX_FUNDS_BACKTEST:
        # backtest mac taa funds vs paper taa indices
        figs, data = run_mac_universe_vs_index_funds_backtest(local_path=local_path,
                                              time_period=time_period,
                                              apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                              meta_params=meta_params,
                                              report_kwargs=report_kwargs)
        qis.save_figs_to_pdf(figs, file_name=f"funds_index_taa", local_path=lp.get_output_path())
        qis.save_df_to_excel(data=data,
                             file_name=f"{file_name}_with_returns",
                             add_current_date=True, local_path=lp.get_output_path())

    elif local_test == LocalTests.PE_SMOOTHING_VS_NEWEY_WEST:
        # backtest mac taa funds vs paper taa indices
        run_mac_pe_smoothed_vs_newey(universe_data=universe_data,
                                     time_period=time_period,
                                     meta_params=meta_params)

    elif local_test == LocalTests.RISK_MODEL_FUTURES_VS_FUNDS_BACKTEST:
        # backtest mac taa funds vs paper taa indices
        run_risk_model_futures_vs_funds_backtest(local_path=local_path,
                                                 time_period=time_period,
                                                 apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                 meta_params=meta_params,
                                                 mac_constraints=mac_constraints)

if __name__ == '__main__':

    run_local_test(local_test=LocalTests.RISK_MODEL_FUTURES_VS_FUNDS_BACKTEST)
