"""
implementation of optimisers for current portfolio and time series backtest
"""
# packages
import pandas as pd
import qis as qis
from typing import Optional, Union, Tuple, Dict
from optimalportfolios import (rolling_risk_budgeting,
                               rolling_maximise_alpha_over_tre,
                               CovarEstimator,
                               compute_joint_alphas,
                               AlphasData,
                               Constraints,
                               EstimatedRollingCovarData)

from mac_portfolio_optimizer import MacUniverseData


def backtest_benchmarked_taa_portfolio(benchmark_rolling_weights: pd.DataFrame,
                                       taa_alphas: pd.DataFrame,
                                       covar_dict: Dict[pd.Timestamp, pd.DataFrame],
                                       joint_prices: pd.DataFrame,
                                       taa_constraints: Constraints,
                                       joint_rebalancing_freq: pd.Series,
                                       time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                       is_apply_tre_utility_objective: bool = False
                                       ) -> pd.DataFrame:
    """
    wrapper for TAA optimisation given benchmark weights and alphas solve tre constraint optimisation
    covar_dict is computed covariance for joint assets
    """
    joint_assets = joint_prices.columns
    # generate rebalancing indicators
    taa_rebalancing_indicators = qis.create_rebalancing_indicators_from_freqs(rebalancing_freqs=joint_rebalancing_freq,
                                                                              time_period=time_period,
                                                                              tickers=joint_assets)
    # align alphas
    taa_alphas = taa_alphas.reindex(index=list(covar_dict.keys()), method='ffill').ffill()
    alphas_joint = taa_alphas.reindex(columns=joint_assets).fillna(0.0)
    # reindex at covar frequency and joint prices columns
    benchmark_rolling_weights = benchmark_rolling_weights.reindex(index=list(covar_dict.keys()), method='ffill').ffill()
    benchmark_rolling_weights = benchmark_rolling_weights.reindex(columns=joint_assets).fillna(0.0)
    taa_rolling_weights = rolling_maximise_alpha_over_tre(prices=joint_prices,
                                                          alphas=alphas_joint,
                                                          constraints0=taa_constraints,
                                                          benchmark_weights=benchmark_rolling_weights,
                                                          covar_dict=covar_dict,
                                                          time_period=time_period,
                                                          rebalancing_indicators=taa_rebalancing_indicators,
                                                          apply_total_to_good_ratio=False,
                                                          is_apply_tre_utility_objective=is_apply_tre_utility_objective)
    return taa_rolling_weights


def backtest_saa_risk_budget_portfolio(universe_data: MacUniverseData,
                                       covar_estimator: CovarEstimator = None,
                                       saa_taa_covar: Dict[pd.Timestamp, pd.DataFrame] = None,
                                       time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                       saa_rebalancing_freq: str = 'QE',
                                       saa_constraints: Constraints = None,
                                       management_fee: float = 0.0,
                                       apply_unsmoothing_for_pe: bool = True,
                                       **kwargs
                                       ) -> Tuple[pd.DataFrame, qis.PortfolioData]:
    """
    implementation for computing saa risk budget portfolio
    use QE or YE for saa_rebalancing_freq
    saa_taa_covar can be passed or calculated on the fly
    """
    saa_rebalancing_schedule = qis.generate_dates_schedule(time_period=time_period, freq=saa_rebalancing_freq)
    saa_risk_prices = universe_data.get_saa_prices(apply_unsmoothing_for_pe=apply_unsmoothing_for_pe)

    if saa_taa_covar is not None:
        saa_assets = universe_data.saa_prices.columns
        saa_pd_covars = {}
        for date in saa_rebalancing_schedule:
            saa_pd_covars[date] = saa_taa_covar[date].loc[saa_assets, saa_assets]
    else:
        # it is important that returns frequency is saa_rebalancing_freq otherwise we cannot compute proper returns of PE and PD
        # estimate covar at rebalancing schedule
        if covar_estimator is None:
            raise ValueError(f"must pass covar_estimator")
        covar_estimator.rebalancing_freq = saa_rebalancing_freq
        rolling_covar_data = covar_estimator.fit_rolling_covars(prices=saa_risk_prices,
                                                                risk_factor_prices=universe_data.get_risk_factors(),
                                                                time_period=time_period)
        covar_dict = rolling_covar_data.y_covars
        # set saa rebalancing freq
        saa_pd_covars = {}
        for date in saa_rebalancing_schedule:
            saa_pd_covars[date] = covar_dict[date]

    # generate rebalancing indicators
    saa_rebalancing_indicators = qis.create_rebalancing_indicators_from_freqs(rebalancing_freqs=saa_rebalancing_freq,
                                                                              time_period=time_period,
                                                                              tickers=universe_data.saa_prices.columns.to_list())

    if saa_constraints is None:
        saa_constraints =  universe_data.get_saa_constraints()
    saa_rolling_weights = rolling_risk_budgeting(prices=saa_risk_prices,
                                                 time_period=time_period,
                                                 covar_dict=saa_pd_covars,
                                                 risk_budget=universe_data.get_saa_risk_budget(),
                                                 constraints0=saa_constraints,
                                                 rebalancing_indicators=saa_rebalancing_indicators,
                                                 apply_total_to_good_ratio=False)  # nb

    saa_portfolio_data = qis.backtest_model_portfolio(prices=universe_data.get_saa_prices(),
                                                      weights=saa_rolling_weights,
                                                      management_fee=management_fee,
                                                      ticker='SAA')
    saa_portfolio_data.covar_dict = saa_pd_covars
    return saa_rolling_weights, saa_portfolio_data


def backtest_saa_taa_portfolios(universe_data: MacUniverseData,
                                covar_estimator: CovarEstimator,
                                time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                is_joint_saa_taa_covar: bool = True,
                                saa_rebalancing_freq: str = 'QE',
                                global_tracking_err_vol_constraint: Optional[float] = None,
                                group_tracking_err_vol_constraint: Optional[pd.Series] = None,
                                global_max_turnover_constraint: Optional[float] = None,
                                group_max_turnover_constraint: Optional[pd.Series] = None,
                                management_fee: float = 0.0,
                                is_saa_benchmark_for_betas: bool = False,
                                rebalancing_costs: float = 0.0,
                                apply_unsmoothing_for_pe: bool = True,
                                ) -> Tuple[qis.MultiPortfolioData, AlphasData, EstimatedRollingCovarData]:
    """
    wrapper for computing saa portfolio and saa-benchmarked taa portfolio
    """
    # 1. estimate covar
    taa_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=universe_data.get_risk_factors(),
                                                        prices=universe_data.get_joint_prices(apply_unsmoothing_for_pe=apply_unsmoothing_for_pe),
                                                        time_period=time_period)
    covar_dict = taa_covar_data.y_covars

    if is_joint_saa_taa_covar:
        saa_taa_covar = covar_dict
    else:
        saa_taa_covar = None

    # 2. run saa
    saa_rolling_weights, saa_portfolio_data = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                 saa_taa_covar=saa_taa_covar,
                                                                                 time_period=time_period,
                                                                                 covar_estimator=covar_estimator,
                                                                                 saa_rebalancing_freq=saa_rebalancing_freq,
                                                                                 management_fee=management_fee,
                                                                                 apply_unsmoothing_for_pe=apply_unsmoothing_for_pe)

    # 3. compute alphas
    if is_saa_benchmark_for_betas:
        benchmark_price = saa_portfolio_data.get_portfolio_nav()
    else:
        benchmark_price = universe_data.benchmarks.iloc[:, 0]
    group_data, _ = universe_data.get_joint_sub_ac_group_data()
    group_data_alphas, _ = universe_data.get_joint_ac_group_data()
    # compute alpha using reported prices
    taa_prices = universe_data.get_taa_prices(apply_unsmoothing_for_pe=apply_unsmoothing_for_pe)
    manager_alphas = compute_joint_alphas(prices=taa_prices,
                                          benchmark_price=benchmark_price,
                                          risk_factors_prices=universe_data.get_risk_factors(),
                                          alpha_beta_type=universe_data.get_alpha_beta_type(),
                                          rebalancing_freq=universe_data.get_joint_rebalancing_freqs(),
                                          estimated_betas=taa_covar_data.asset_last_betas_t,
                                          group_data_alphas=universe_data.get_taa_asset_class_data(is_merge_alts_with_equity=True),
                                          return_annualisation_freq_dict=universe_data.return_annualisation_freq_dict)

    # 4. run tre portfolio
    taa_constraints = universe_data.get_taa_constraints(
        global_tracking_err_vol_constraint=global_tracking_err_vol_constraint,
        group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
        global_max_turnover_constraint=global_max_turnover_constraint,
        group_max_turnover_constraint=group_max_turnover_constraint)

    taa_rolling_weights = backtest_benchmarked_taa_portfolio(benchmark_rolling_weights=saa_rolling_weights,
                                                             taa_alphas=manager_alphas.alpha_scores,
                                                             joint_prices=universe_data.get_joint_prices(),
                                                             joint_rebalancing_freq=universe_data.get_joint_rebalancing_freqs(),
                                                             covar_dict=covar_dict,
                                                             time_period=time_period,
                                                             taa_constraints=taa_constraints)
    prices = universe_data.get_joint_prices()
    taa_portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                      weights=taa_rolling_weights,
                                                      management_fee=management_fee,
                                                      rebalancing_costs=rebalancing_costs,
                                                      ticker='TAA')
    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=[taa_portfolio_data, saa_portfolio_data],
                                                  benchmark_prices=universe_data.benchmarks,
                                                  covar_dict=covar_dict)
    group_data, group_order = universe_data.get_joint_sub_ac_group_data()
    [x.set_group_data(group_data=group_data, group_order=group_order) for x in multi_portfolio_data.portfolio_datas]
    return multi_portfolio_data, manager_alphas, taa_covar_data


def range_backtest_lasso_portfolio_with_alphas(universe_data: MacUniverseData,
                                               covar_estimator: CovarEstimator,
                                               time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                               is_joint_saa_taa_covar: bool = True,
                                               saa_rebalancing_freq: Union[str, pd.Series] = 'QE',
                                               global_tracking_err_vol_constraint: Optional[float] = None,
                                               group_tracking_err_vol_constraint: Optional[pd.Series] = None,
                                               global_max_turnover_constraint: Optional[float] = None,
                                               group_max_turnover_constraint: Optional[pd.Series] = None,
                                               management_fee: float = 0.0,
                                               is_saa_benchmark_for_betas: bool = False,
                                               rebalancing_costs: float = 0.0,
                                               ) -> (qis.MultiPortfolioData, qis.MultiPortfolioData):

    spans = [24]  # span, squeeze_factor
    # reg_lambdas = [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]
    reg_lambdas = [1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 0.0]
    # reg_lambdas = [5.0*1e-5, 5.0*1e-6, 5.0*1e-7]
    # reg_lambdas = [5.0 * 1e-4, 1e-4, 5.0 * 1e-5, 1e-5, 5.0 * 1e-6, 1e-6]
    squeeze_factors = [0.0]

    saa_portfolio_datas = []
    taa_portfolio_datas = []
    for span in spans:
        for squeeze_factor in squeeze_factors:
            for reg_lambda in reg_lambdas:
                ticker = f"span={span:0.0f}, lambda={reg_lambda:0.0e}, sqze={squeeze_factor:0.2f}"
                covar_estimator.lasso_model.reg_lambda = reg_lambda
                covar_estimator.lasso_model.span = span
                covar_estimator.span_freq_dict = {'ME': span, 'QE': span / 4}
                multi_portfolio_data, _, _ = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                      time_period=time_period,
                                                                      covar_estimator=covar_estimator,
                                                                      is_joint_saa_taa_covar=is_joint_saa_taa_covar,
                                                                      saa_rebalancing_freq=saa_rebalancing_freq,
                                                                      is_saa_benchmark_for_betas=is_saa_benchmark_for_betas,
                                                                      global_tracking_err_vol_constraint=global_tracking_err_vol_constraint,
                                                                      group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                                                                      global_max_turnover_constraint=global_max_turnover_constraint,
                                                                      group_max_turnover_constraint=group_max_turnover_constraint,
                                                                      rebalancing_costs=rebalancing_costs,
                                                                      management_fee=management_fee)
                saa_portfolio_datas.append(multi_portfolio_data.portfolio_datas[1].set_ticker(ticker))
                taa_portfolio_datas.append(multi_portfolio_data.portfolio_datas[0].set_ticker(ticker))

    saa_multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=saa_portfolio_datas,
                                                      benchmark_prices=universe_data.benchmarks.iloc[:, 0])
    taa_multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=taa_portfolio_datas,
                                                      benchmark_prices=universe_data.benchmarks.iloc[:, 0])
    return saa_multi_portfolio_data, taa_multi_portfolio_data


def tre_range_backtest_lasso_portfolio_with_alphas(universe_data: MacUniverseData,
                                                   covar_estimator: CovarEstimator,
                                                   time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                                   saa_rebalancing_freq: str = 'QE',
                                                   management_fee: float = 0.0,
                                                   is_saa_benchmark_for_betas: bool = False,
                                                   rebalancing_costs: float = 0.0,
                                                   is_grouped_constaints: bool = True
                                                   ) -> (qis.MultiPortfolioData, qis.MultiPortfolioData):

    tracking_err_vol_constraints = [0.025]
    turnover_constraints = [0.125, 0.25, 0.5]

    saa_portfolio_datas = []
    taa_portfolio_datas = []
    for tracking_err_vol_constraint in tracking_err_vol_constraints:
        for turnover_constraint in turnover_constraints:
            if is_grouped_constaints:
                ticker = f"group_tre_vol={tracking_err_vol_constraint:0.2%}, turnover={turnover_constraint:0.2%}"
                group_tracking_err_vol_constraint = universe_data.set_group_uniform_tracking_error_constraint(tracking_err_vol_constraint=tracking_err_vol_constraint)
                global_tracking_err_vol_constraint = None
            else:
                ticker = f"global_tre_vol={tracking_err_vol_constraint:0.2%}, turnover={turnover_constraint:0.2%}"
                global_tracking_err_vol_constraint = tracking_err_vol_constraint
                group_tracking_err_vol_constraint = None

            multi_portfolio_data, _, _ = backtest_saa_taa_portfolios(universe_data=universe_data,
                                                                  time_period=time_period,
                                                                  covar_estimator=covar_estimator,
                                                                  saa_rebalancing_freq=saa_rebalancing_freq,
                                                                  global_tracking_err_vol_constraint=global_tracking_err_vol_constraint,
                                                                  group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                                                                  global_max_turnover_constraint=turnover_constraint,
                                                                  group_max_turnover_constraint=None,
                                                                  management_fee=management_fee,
                                                                  is_saa_benchmark_for_betas=is_saa_benchmark_for_betas,
                                                                  rebalancing_costs=rebalancing_costs)
            saa_portfolio_datas.append(multi_portfolio_data.portfolio_datas[1].set_ticker(ticker))
            taa_portfolio_datas.append(multi_portfolio_data.portfolio_datas[0].set_ticker(ticker))

    saa_multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=saa_portfolio_datas,
                                                      benchmark_prices=universe_data.benchmarks.iloc[:, 0])
    taa_multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas=taa_portfolio_datas,
                                                      benchmark_prices=universe_data.benchmarks.iloc[:, 0])
    return saa_multi_portfolio_data, taa_multi_portfolio_data
