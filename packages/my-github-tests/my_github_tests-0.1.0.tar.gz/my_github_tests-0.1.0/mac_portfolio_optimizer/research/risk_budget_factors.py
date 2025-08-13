"""
run backtest for different specs of risk budget
"""
# packages

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import qis as qis
from typing import Optional, Tuple
from enum import Enum

from optimalportfolios import (estimate_rolling_lasso_covar_different_freq,
                               wrapper_risk_budgeting,
                               GroupLowerUpperConstraints,
                               wrapper_maximise_alpha_over_tre,
                               CovarEstimator,
                               EstimatedRollingCovarData)

# project
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
                                     get_meta_params,
                                     backtest_saa_risk_budget_portfolio)


def run_given_date_optimisation(universe_data: MacUniverseData):

    time_period = qis.TimePeriod('31Dec2021', '30Jun2025')

    # set model params
    covar_estimator = get_prod_covar_estimator(rebalancing_freq='YE',
                                               apply_unsmoothing_for_pe=True,
                                               returns_freqs=universe_data.get_joint_rebalancing_freqs())
    # estimate covar data
    covar_data = estimate_rolling_lasso_covar_different_freq(risk_factor_prices=universe_data.get_risk_factors(),
                                                             prices=universe_data.get_saa_prices(apply_unsmoothing_for_pe=True),
                                                             returns_freqs=universe_data.get_saa_rebalancing_freqs(),
                                                             time_period=time_period,
                                                             factor_returns_freq='ME',
                                                             rebalancing_freq='YE',
                                                             lasso_model=covar_estimator.lasso_model)
    # print available dates
    print(f"rebalancing dates={covar_data.y_covars.keys()}")
    optimisation_date = pd.Timestamp('2022-12-31')

    # solver risk budget problem
    risk_budget = universe_data.get_saa_risk_budget()
    pd_covar = covar_data.y_covars[optimisation_date]
    constraints0=universe_data.get_saa_constraints()
    risk_budget_weights = wrapper_risk_budgeting(pd_covar=pd_covar,
                                                 constraints0=constraints0,
                                                 risk_budget=risk_budget)

    # betas
    asset_betas = covar_data.asset_last_betas_t[optimisation_date]
    print(asset_betas)

    # create exposure constraints
    group_min_allocation = pd.Series({'Equity': 0.0, 'Bond': 0.0, 'Credit': 0.0, 'PE premia': 0.0, 'Liquidity premia': 0.0, 'Inflation premia': 0.0})
    group_max_allocation = pd.Series({'Equity': 0.30, 'Bond': 0.3, 'Credit': 0.3, 'PE premia': 0.3, 'Liquidity premia': 0.3, 'Inflation premia': 0.3})
    factor_constraints = GroupLowerUpperConstraints(group_loadings=asset_betas.T,
                                                    group_min_allocation=group_min_allocation,
                                                    group_max_allocation=group_max_allocation)
    constraints1 = constraints0.update_group_lower_upper_constraints(group_lower_upper_constraints=factor_constraints)

    # solve rb with new constraint
    risk_budget_weights1 = wrapper_risk_budgeting(pd_covar=pd_covar,
                                                 constraints0=constraints1,
                                                 risk_budget=risk_budget)

    weight2 = wrapper_maximise_alpha_over_tre(pd_covar=pd_covar,
                                              alphas=None,
                                              benchmark_weights=risk_budget_weights,
                                              constraints0=constraints1,
                                              verbose=True)

    # plots
    qis.plot_corr_matrix_from_covar(covar=pd_covar)
    qis.plot_heatmap(df=asset_betas.where(np.abs(asset_betas)>1e-4, other=np.nan).T,
                     title='asset betas', var_format='{:,.2f}')


    df = pd.concat([risk_budget.rename('risk-budget'),
                    risk_budget_weights.rename('rb0 weight'),
                    risk_budget_weights1.rename('rb1 weight'),
                    weight2.rename('min tre')],
                   axis=1)
    print(df)
    qis.plot_df_table(df=df, var_format='{:,.2%}', title='portfolio weights')

    factor_exposures0 = asset_betas @ risk_budget_weights
    factor_exposures1 = asset_betas @ risk_budget_weights1
    factor_exposures2 = asset_betas @ weight2
    df = pd.concat([factor_exposures0.rename('rb0'),
                    factor_exposures1.rename('rb1'),
                    factor_exposures2.rename('rb2')],
                   axis=1)
    print(df)
    qis.plot_df_table(df=df, var_format='{:,.2f}', title='factor exposures')

    # qis.plot_bars(df=risk_budget_weights, var_format='{:,.2%}', title='rb weights', legend_loc=None)


def rolling_backtest(universe_data: MacUniverseData,
                     covar_estimator: CovarEstimator,
                     factor_min_exposure: Optional[pd.Series],
                     factor_max_exposure: pd.Series,
                     time_period: qis.TimePeriod,
                     apply_unsmoothing_for_pe: bool = True
                     )-> Tuple[qis.MultiPortfolioData, EstimatedRollingCovarData]:

    taa_covar_data = covar_estimator.fit_rolling_covars(prices=universe_data.get_saa_prices(apply_unsmoothing_for_pe=apply_unsmoothing_for_pe),
                                                            risk_factor_prices=universe_data.get_risk_factors(),
                                                            time_period=time_period)
    covar_dict = taa_covar_data.y_covars

    constraints0 = universe_data.get_saa_constraints()
    saa_rolling_weights, saa_portfolio_data = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                 time_period=time_period,
                                                                                 saa_taa_covar=covar_dict,
                                                                                 apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                                                                 saa_constraints=constraints0,
                                                                                 saa_rebalancing_freq=covar_estimator.rebalancing_freq)
    print(saa_rolling_weights)

    # betas
    constraints0.group_lower_upper_constraints = constraints0.group_lower_upper_constraints.drop_constraint(name='Equity')
    tre_weights = {}
    for date, pd_covar in covar_dict.items():
        asset_betas = taa_covar_data.asset_last_betas_t[date]
        # create exposure constraints
        factor_constraints = GroupLowerUpperConstraints(group_loadings=asset_betas.T,
                                                        group_min_allocation=factor_min_exposure,
                                                        group_max_allocation=factor_max_exposure)
        constraints1 = constraints0.update_group_lower_upper_constraints(group_lower_upper_constraints=factor_constraints,
                                                                         filling_value_for_missing_lower_bound=0.0)
        tre_weights[date] = wrapper_maximise_alpha_over_tre(pd_covar=pd_covar,
                                                            alphas=None,
                                                            benchmark_weights=saa_rolling_weights.loc[date, :],
                                                            constraints0=constraints1)
    tre_weights = pd.DataFrame.from_dict(tre_weights, orient='index')
    print(tre_weights)

    prices = universe_data.get_saa_prices()
    saa_portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                      weights=saa_rolling_weights,
                                                      ticker='RiskBudget')
    tre_portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                      weights=tre_weights,
                                                      ticker='TRE constraint')
    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[saa_portfolio_data, tre_portfolio_data],
                                                  benchmark_prices=universe_data.benchmarks,
                                                  covar_dict=covar_dict)
    group_data, group_order = universe_data.get_saa_asset_class_data(), universe_data.ac_group_order
    [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]
    return multi_portfolio_data, taa_covar_data


class LocalTests(Enum):
    GIVEN_DATE_OPTIMISATION = 1
    ROLLING_BACKTEST = 2


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
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER,
                                                    risk_model=RiskModel.FUTURES_RISK_FACTORS)

    # set lasso model params
    saa_rebalancing_freq = 'YE'
    apply_unsmoothing_for_pe = True
    returns_freqs = universe_data.get_joint_rebalancing_freqs()
    covar_estimator = get_prod_covar_estimator(rebalancing_freq=saa_rebalancing_freq,
                                               apply_unsmoothing_for_pe=apply_unsmoothing_for_pe,
                                               returns_freqs=returns_freqs)

    if local_test == LocalTests.GIVEN_DATE_OPTIMISATION:
        run_given_date_optimisation(universe_data=universe_data)

        plt.show()

    elif local_test == LocalTests.ROLLING_BACKTEST:

        time_period = qis.TimePeriod('31Dec2016', '31Mar2025')

        factor_min_exposure = pd.Series({'Equity': 0.0, 'Bond': 0.0, 'Credit': 0.0, 'PE premia': 0.0, 'Liquidity premia': 0.0, 'Inflation premia': 0.0})
        factor_max_exposure = pd.Series({'Equity': 0.7, 'Bond': 0.5, 'Credit': 0.5, 'PE premia': 0.5, 'Liquidity premia': 0.01, 'Inflation premia': 0.5})
        multi_portfolio_data, taa_covar_data = rolling_backtest(universe_data=universe_data,
                                                                covar_estimator=covar_estimator,
                                                                factor_min_exposure=factor_min_exposure,
                                                                factor_max_exposure=factor_max_exposure,
                                                                time_period=time_period)
        generate_report(multi_portfolio_data=multi_portfolio_data,
                        taa_covar_data=taa_covar_data,
                        universe_data=universe_data,
                        time_period=time_period,
                        apply_sub_ac_group_data=False,
                        save_excel=False,
                        file_name=f"rolling_rb_tre_backtest",
                        local_path=lp.get_output_path())


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.ROLLING_BACKTEST)
