import pandas as pd
import numpy as np
import qis as qis
from typing import Dict, Tuple
from enum import Enum

from optimalportfolios import (CovarEstimator,
                               rolling_risk_budgeting,
                               solve_for_risk_budgets_from_given_weights)

from mac_portfolio_optimizer import local_path as lp

from mac_portfolio_optimizer import (get_prod_covar_estimator, load_mac_portfolio_universe,
                                     MacUniverseData,
                                     SaaPortfolio,
                                     SaaRangeConstraints)


FEEDER_EXCEL_FILE1 = 'Step 1 SAA - Artur'


class ApacMandates(Enum):
    INCOME = (SaaPortfolio.APAC_INCOME, SaaRangeConstraints.APAC_INCOME)
    CONSERVATIVE = (SaaPortfolio.APAC_CONSERVATIVE, SaaRangeConstraints.APAC_CONSERVATIVE)
    BALANCED = (SaaPortfolio.APAC_BALANCED, SaaRangeConstraints.APAC_BALANCED)
    GROWTH = (SaaPortfolio.APAC_GROWTH, SaaRangeConstraints.APAC_GROWTH)
    EQUITIES = (SaaPortfolio.APAC_EQUITIES, SaaRangeConstraints.APAC_EQUITIES)


def load_range_mandate(local_path: str,
                       excel_feeder_file: str = FEEDER_EXCEL_FILE1,
                       mandate: ApacMandates = ApacMandates.BALANCED
                       ) -> MacUniverseData:
    mac_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=mandate.value[0],
                                                    taa_portfolio=None,
                                                    saa_range_constraints=mandate.value[1],
                                                    file_name=excel_feeder_file)
    return mac_universe_data


def solve_risk_budget_for_mandate(universe_data: MacUniverseData,
                                  covar_estimator: CovarEstimator,
                                  covar_dict: Dict[pd.Timestamp, pd.DataFrame] = None,
                                  time_period: qis.TimePeriod = qis.TimePeriod('31Dec2004', None),
                                  saa_rebalancing_freq: str = 'YE'
                                  ) -> Tuple[pd.DataFrame, pd.DataFrame, qis.MultiPortfolioData]:
    # 1. estimate covar
    if covar_dict is None:
        covar_estimator.rebalancing_freq = saa_rebalancing_freq
        taa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=universe_data.get_risk_factors(),
                                                            prices=universe_data.saa_prices,
                                                            time_period=time_period)
        covar_dict = taa_covar_data.y_covars
    # risk-budget portfolio
    saa_target_weights = universe_data.get_benchmark_static_weights()
    risk_budget = solve_for_risk_budgets_from_given_weights(prices=universe_data.saa_prices,
                                                            given_weights=saa_target_weights,
                                                            time_period=time_period,
                                                            covar_dict=covar_dict)
    # run backtest
    saa_constraints = universe_data.get_saa_constraints()
    saa_rolling_weights = rolling_risk_budgeting(prices=universe_data.saa_prices,
                                                 time_period=time_period,
                                                 covar_dict=covar_dict,
                                                 risk_budget=risk_budget,
                                                 constraints0=saa_constraints,
                                                 rebalancing_indicators=None,
                                                 apply_total_to_good_ratio=False)  # nb
    saa_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices, weights=saa_rolling_weights,
                                                      management_fee=0.0,
                                                      ticker='SAA Risk-Budgeted')

    # 2. benchmark with static weights
    benchmark_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.saa_prices,
                                                      weights=saa_target_weights,
                                                      rebalancing_freq=saa_rebalancing_freq,
                                                      management_fee=0.0,
                                                      ticker='SAA Static Weight')

    # multiportfolio including benchmark
    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio_data, benchmark_portfolio_data],
                                                  benchmark_prices=universe_data.benchmarks,
                                                  covar_dict=covar_dict)
    group_data, group_order = universe_data.get_joint_sub_ac_group_data()
    [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]

    risk_budget_df = pd.concat([risk_budget.rename('Inferred risk budget'),
                                saa_target_weights.rename('SAA target teight'),
                                saa_rolling_weights.replace({0.0: np.nan}).mean(0).rename('SAA Avg weight')],
                               axis=1)

    return risk_budget_df, saa_rolling_weights, multi_portfolio_data


def run_all_mandates(local_path: str,
                     covar_estimator: CovarEstimator,
                     time_period: qis.TimePeriod = qis.TimePeriod('31Dec2004', None),
                     saa_rebalancing_freq: str = 'YE'
                     ) -> Tuple[Dict, Dict]:

    # 1. estimate covar for all
    covar_estimator.rebalancing_freq = saa_rebalancing_freq
    universe_data = load_range_mandate(local_path=local_path, mandate=ApacMandates.BALANCED)
    taa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=universe_data.get_risk_factors(),
                                                        prices=universe_data.saa_prices,
                                                        time_period=time_period)
    covar_dict = taa_covar_data.y_covars

    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)

    risk_budgets_dfs = {}
    figs = {}
    for mandate in list(ApacMandates):
        universe_data = load_range_mandate(local_path=local_path, mandate=mandate)
        risk_budgets_df, saa_rolling_weights, multi_portfolio_data = solve_risk_budget_for_mandate(universe_data=universe_data,
                                                                                                   covar_estimator=covar_estimator,
                                                                                                   time_period=time_period,
                                                                                                   covar_dict=covar_dict,
                                                                                                   saa_rebalancing_freq=saa_rebalancing_freq)
        key = mandate.name.lower()
        risk_budgets_dfs[f"{key}-rb"] = risk_budgets_df
        risk_budgets_dfs[f"{key}-weights"] = saa_rolling_weights
        figs[key] = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                                  add_benchmarks_to_navs=True,
                                                                  add_exposures_comp=False,
                                                                  add_strategy_factsheet=True,
                                                                  time_period=time_period,
                                                                  **report_kwargs)
        print(key)
        print(risk_budgets_df)

    return risk_budgets_dfs, figs


class LocalTests(Enum):
    LOAD_RANGE_MANDATE = 1
    ESTIMATE_RISK_BUDGETS = 2
    RUN_ALL_MANDATES = 3


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    local_path = lp.get_resource_path()
    time_period = qis.TimePeriod('31Dec2004', '30Jun2025')
    saa_rebalancing_freq = 'YE'
    covar_estimator = get_prod_covar_estimator(rebalancing_freq=saa_rebalancing_freq)

    if local_test == LocalTests.LOAD_RANGE_MANDATE:
        mac_universe_data = load_range_mandate(local_path=local_path)
        this = mac_universe_data.get_saa_constraints()
        print(this)

    elif local_test == LocalTests.ESTIMATE_RISK_BUDGETS:
        mandate = ApacMandates.BALANCED
        universe_data = load_range_mandate(local_path=local_path, mandate=mandate)
        risk_budget, saa_rolling_weights, multi_portfolio_data = solve_risk_budget_for_mandate(universe_data=universe_data,
                                                                                               covar_estimator=covar_estimator,
                                                                                               time_period=time_period,
                                                                                               saa_rebalancing_freq=saa_rebalancing_freq)
        print(risk_budget)

        report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                        reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                        add_rates_data=False)
        figs1 = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                              add_benchmarks_to_navs=True,
                                                              add_exposures_comp=False,
                                                              add_strategy_factsheet=True,
                                                              time_period=time_period,
                                                              **report_kwargs)
        qis.save_figs_to_pdf(figs1, file_name=f"{mandate.name}_risk_budgets", local_path=lp.get_output_path())

    elif local_test == LocalTests.RUN_ALL_MANDATES:
        risk_budgets_dfs, figs = run_all_mandates(local_path=lp.get_resource_path(),
                                                  covar_estimator=covar_estimator,
                                                  time_period=time_period,
                                                  saa_rebalancing_freq=saa_rebalancing_freq)
        qis.save_df_to_excel(data=risk_budgets_dfs, file_name='apac_mandates_budgets', add_current_date=True,
                             local_path=lp.get_output_path())
        for key, figs_ in figs.items():
            qis.save_figs_to_pdf(figs_, file_name=f"{key}", local_path=lp.get_output_path())


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.RUN_ALL_MANDATES)
