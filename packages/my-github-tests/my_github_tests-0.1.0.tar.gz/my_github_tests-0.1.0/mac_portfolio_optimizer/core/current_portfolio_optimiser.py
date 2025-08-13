"""
optimisation engine for the current portfolio
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import qis as qis
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
from optimalportfolios import (CovarEstimator,
                               EstimatedCurrentCovarData,
                               EstimatedRollingCovarData,
                               wrapper_risk_budgeting,
                               compute_joint_alphas,
                               wrapper_maximise_alpha_over_tre)

from mac_portfolio_optimizer import MacUniverseData, backtest_saa_risk_budget_portfolio


@dataclass
class SaaTaaPortfolios:
    """
    output of current saa and taa portfolios
    """
    saa_valuation_date: pd.Timestamp
    taa_valuation_date: pd.Timestamp
    taa_df: pd.DataFrame
    taa_covar: pd.DataFrame
    saa_df: pd.DataFrame
    saa_covar: pd.DataFrame
    universe_data: MacUniverseData
    taa_rolling_covar_data: EstimatedRollingCovarData
    saa_current_covar_data: Optional[EstimatedCurrentCovarData]

    taa_corr: pd.DataFrame = None
    saa_corr: pd.DataFrame = None

    def __post_init__(self):
        self.taa_corr = qis.covar_to_corr(covar=self.taa_covar)
        self.saa_corr = qis.covar_to_corr(covar=self.saa_covar)

    def get_output_dict(self,
                        period_2y: qis.TimePeriod = qis.TimePeriod('31Dec2022', '31Dec2024'),
                        period_5y: qis.TimePeriod = qis.TimePeriod('31Dec2019', '31Dec2024'),
                        saa_kwargs: Dict[str, Any] = dict(perf_params=qis.PerfParams(freq='QE'), alpha_an_factor=4.0),
                        taa_kwargs: Dict[str, Any] = dict(perf_params=qis.PerfParams(freq='QE'), alpha_an_factor=4.0)
                        ) -> Dict[str, pd.DataFrame]:
        """
        produce outputs dfs
        """
        taa_df = self.taa_df.copy()
        saa_df = self.saa_df.copy()

        saa_prices = pd.concat([self.universe_data.benchmarks, self.universe_data.saa_prices], axis=1)
        saa_perf_2y = qis.get_ra_perf_benchmark_columns(prices=period_2y.locate(saa_prices),
                                                        benchmark=self.universe_data.benchmarks.columns[0],
                                                        is_convert_to_str=False,
                                                        **saa_kwargs)
        saa_perf_5y = qis.get_ra_perf_benchmark_columns(prices=period_5y.locate(saa_prices),
                                                        benchmark=self.universe_data.benchmarks.columns[0],
                                                        is_convert_to_str=False,
                                                        **saa_kwargs)

        taa_prices = pd.concat([self.universe_data.benchmarks, self.universe_data.taa_prices], axis=1)
        taa_perf_2y = qis.get_ra_perf_benchmark_columns(prices=period_2y.locate(taa_prices),
                                                        benchmark=self.universe_data.benchmarks.columns[0],
                                                        is_convert_to_str=False,
                                                        **taa_kwargs)
        taa_perf_5y = qis.get_ra_perf_benchmark_columns(prices=period_5y.locate(taa_prices),
                                                        benchmark=self.universe_data.benchmarks.columns[0],
                                                        is_convert_to_str=False,
                                                        **taa_kwargs)

        # betas
        taa_betas = self.taa_rolling_covar_data.asset_last_betas_t[self.taa_valuation_date].T.loc[taa_df.index]
        saa_betas = self.taa_rolling_covar_data.asset_last_betas_t[self.saa_valuation_date].T.loc[saa_df.index]

        # taa r2
        taa_df['r2'] = self.taa_rolling_covar_data.r2_pd[taa_df.index].iloc[-1, :]

        # add betas
        taa_df = pd.concat([taa_df, taa_betas], axis=1)

        # taa vols
        ewma_vol = qis.compute_ewm_vol(data=qis.to_returns(prices=taa_prices, is_log_returns=True),
                                       mean_adj_type=qis.MeanAdjType.EWMA, span=24, annualization_factor=12)
        taa_df['lasso-vol'] = np.sqrt(np.diag(self.taa_covar))  # todo
        taa_df['ewm-vol'] = ewma_vol.iloc[-1, :]
        taa_df['vol 2y'] = taa_perf_2y['Vol'].loc[taa_df.index]

        # merge with universe taa data
        taa_universe_df = self.universe_data.taa_universe_df.copy()
        if 'Current Max' in taa_universe_df.columns:  # remove level 2 attributions
            col_index = taa_universe_df.columns.get_loc('Current Max')
            columns_to_keep = taa_universe_df.columns[:col_index + 1]
            taa_universe_df = taa_universe_df[columns_to_keep]

        taa_df = pd.concat([taa_universe_df, taa_df, ], axis=1)
        # saa r2 and vols
        saa_df['r2'] = self.taa_rolling_covar_data.r2_pd[saa_df.index].iloc[-1, :]
        saa_df['lasso-vol'] = np.sqrt(np.diag(self.saa_covar))
        saa_df['vol 5y'] = saa_perf_5y['Vol'].loc[saa_df.index]

        data = dict(taa_df=taa_df,
                    saa_df=saa_df,
                    taa_perf_2y=taa_perf_2y,
                    taa_perf_5y=taa_perf_5y,
                    saa_perf_2y=saa_perf_2y,
                    saa_perf_5y=saa_perf_5y,
                    taa_corr=self.taa_corr,
                    saa_corr=self.saa_corr,
                    taa_betas=taa_betas,
                    saa_betas=saa_betas)
        return data

    def plot_taa_corr(self, **kwargs) -> plt.Subplot:
        df = self.taa_corr
        with sns.axes_style('darkgrid'):
            width, height = qis.get_df_table_size(df=df)
            fig, ax = plt.subplots(1, 1, figsize=(width, width), constrained_layout=True)
            qis.plot_heatmap(df=df,
                             var_format='{:.2f}',
                             cmap='PiYG',
                             ax=ax,
                             **kwargs)
        return fig


def run_current_saa_portfolio(universe_data: MacUniverseData,
                              covar_estimator: CovarEstimator,
                              saa_pd_covar: pd.DataFrame = None,
                              saa_valuation_date: pd.Timestamp = pd.Timestamp('31Dec2024'),
                              saa_rebalancing_indicators: pd.Series = None  # for PE
                              ) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[EstimatedCurrentCovarData]]:
    """
    use QE or YE for saa_rebalancing_freq
    """
    if saa_pd_covar is None:
        saa_covar_data = covar_estimator.fit_current_covars(
            risk_factor_prices=universe_data.get_risk_factors().loc[:saa_valuation_date, :],
            prices=universe_data.get_joint_prices().loc[:saa_valuation_date, :])
        saa_pd_covar = saa_covar_data.y_covar
    else:
        saa_covar_data = None

    saa_outputs = wrapper_risk_budgeting(pd_covar=saa_pd_covar,
                                         constraints0=universe_data.get_saa_constraints(),
                                         weights_0=None,
                                         risk_budget=universe_data.get_saa_risk_budget(),
                                         rebalancing_indicators=saa_rebalancing_indicators,
                                         apply_total_to_good_ratio=False,
                                         detailed_output=True)
    return saa_outputs, saa_pd_covar, saa_covar_data


def run_current_saa_taa_portfolios(universe_data: MacUniverseData,
                                   covar_estimator: CovarEstimator,
                                   saa_valuation_date: pd.Timestamp = pd.Timestamp('31Dec2024'),
                                   taa_valuation_date: pd.Timestamp = pd.Timestamp('28Feb2024'),
                                   time_period: qis.TimePeriod = qis.TimePeriod('31Dec2003', None),
                                   saa_rebalancing_freq: str = 'QE',
                                   taa_weights_0: pd.Series = None,
                                   is_joint_saa_taa_covar: bool = True,
                                   taa_rebalancing_indicators: pd.Series = None,
                                   global_tracking_err_vol_constraint: Optional[float] = None,
                                   group_tracking_err_vol_constraint: Optional[pd.Series] = None,
                                   global_max_turnover_constraint: float = None,
                                   group_max_turnover_constraint: Optional[pd.Series] = None,
                                   is_saa_benchmark_for_betas: bool = True,
                                   use_current_min_max: bool = True
                                   ) -> SaaTaaPortfolios:
    """
    optimisation of the current saa_taa portfolio
    taa_weights_0 are provided in universe_data
    taa_weights_0 = universe_data.get_taa_current_weights()
    """
    # 1. estimate rolling covar for taa and betas
    # we need betas time series to estiate alphas
    risk_factor_prices = universe_data.get_risk_factors().loc[:taa_valuation_date, :]
    taa_rolling_covar_data = covar_estimator.fit_rolling_covars(risk_factor_prices=risk_factor_prices,
                                                                prices=universe_data.get_joint_prices().loc[:taa_valuation_date, :],
                                                                time_period=time_period)
    if is_joint_saa_taa_covar:
        saa_taa_covar = taa_rolling_covar_data.y_covars
        if saa_valuation_date not in saa_taa_covar.keys():
            raise KeyError(f"{saa_valuation_date} not in {saa_taa_covar.keys()}")
        saa_assets = universe_data.saa_prices.columns
        saa_pd_covar = saa_taa_covar[saa_valuation_date].loc[saa_assets, saa_assets]
    else:
        raise NotImplementedError

    # construct saa portfolio: we need saa portfolio weights for benchmark calculation and low beta characteristics
    saa_rebalancing_indicators = qis.create_rebalancing_indicators_from_freqs(rebalancing_freqs=saa_rebalancing_freq,
                                                                              time_period=time_period,
                                                                              tickers=universe_data.saa_prices.columns.to_list())
    saa_rolling_weights, saa_portfolio_data = backtest_saa_risk_budget_portfolio(universe_data=universe_data,
                                                                                 saa_taa_covar=saa_taa_covar,
                                                                                 time_period=time_period,
                                                                                 covar_estimator=covar_estimator,
                                                                                 saa_rebalancing_freq=saa_rebalancing_freq,
                                                                                 management_fee=0.0)
    # to do: use saa_rolling_weights
    saa_df, saa_pd_covar, saa_current_covar_data = run_current_saa_portfolio(universe_data=universe_data,
                                                                             covar_estimator=covar_estimator,
                                                                             saa_pd_covar=saa_pd_covar,
                                                                             saa_valuation_date=saa_valuation_date,
                                                                             saa_rebalancing_indicators=saa_rebalancing_indicators.loc[saa_valuation_date, :])
    rebalancing_freq = universe_data.get_joint_rebalancing_freqs()

    current_saa_weights = saa_df['weights']
    saa_df = saa_df.rename({'weights': 'SAA weight'}, axis=1)

    # 2. compute alphas
    if is_saa_benchmark_for_betas:
        benchmark_price = saa_portfolio_data.get_portfolio_nav()
    else:
        benchmark_price = universe_data.benchmarks.iloc[:, 0]

    joint_alphas = compute_joint_alphas(prices=universe_data.taa_prices,
                                        benchmark_price=benchmark_price,
                                        risk_factors_prices=universe_data.get_risk_factors(),
                                        alpha_beta_type=universe_data.get_alpha_beta_type(),
                                        rebalancing_freq=rebalancing_freq,
                                        estimated_betas=taa_rolling_covar_data.asset_last_betas_t,
                                        group_data_alphas=universe_data.get_taa_asset_class_data(is_merge_alts_with_equity=True),
                                        return_annualisation_freq_dict=universe_data.return_annualisation_freq_dict)

    # 3. run tre portfolio
    if taa_weights_0 is None:
        taa_weights_0 = universe_data.get_taa_current_weights()
    taa_constraints = universe_data.get_taa_constraints(use_current_min_max=use_current_min_max,
                                                        global_tracking_err_vol_constraint=global_tracking_err_vol_constraint,
                                                        group_tracking_err_vol_constraint=group_tracking_err_vol_constraint,
                                                        global_max_turnover_constraint=global_max_turnover_constraint,
                                                        group_max_turnover_constraint=group_max_turnover_constraint)

    # extend alphas and weights
    taa_assets = universe_data.taa_prices.columns.to_list()
    taa_covar = taa_rolling_covar_data.y_covars[taa_valuation_date].loc[taa_assets, taa_assets]
    if taa_rebalancing_indicators is not None:
        rebalancing_indicators = taa_rebalancing_indicators.reindex(index=taa_assets).fillna(0)
    else:
        rebalancing_indicators = pd.Series(1, index=taa_assets)
    current_taa_weights = wrapper_maximise_alpha_over_tre(pd_covar=taa_covar,
                                                          alphas=joint_alphas.alpha_scores.loc[taa_valuation_date, :],
                                                          constraints0=taa_constraints,
                                                          benchmark_weights=current_saa_weights,
                                                          weights_0=taa_weights_0,
                                                          rebalancing_indicators=rebalancing_indicators,
                                                          apply_total_to_good_ratio=False,
                                                          detailed_output=True)

    taa_weights = current_taa_weights['weights'].loc[taa_assets].rename('Taa Weights')
    # do few round rounding to converge to weights with 2 decimals
    for n in np.arange(5):
        taa_weights = taa_weights / np.nansum(taa_weights)
        taa_weights = taa_weights.round(decimals=4)

    if taa_weights_0 is not None:
        taa_weights0 = taa_weights_0.loc[universe_data.taa_prices.columns].rename('Given Taa Weights')
    else:
        taa_weights0 = pd.Series(0.0, index=universe_data.taa_prices.columns).rename('Given Taa Weights')

    taa_rebalancing_indicator = rebalancing_indicators.rename('Is Rebalanced')
    delta = taa_weights.subtract(taa_weights0).rename('Delta weights')
    alphas = joint_alphas.get_alphas_snapshot(date=taa_valuation_date)
    risk_contribs = current_taa_weights['asset_rc_ratio'].loc[taa_assets].rename('Risk Contribution')
    taa_df = pd.concat([taa_rebalancing_indicator, taa_weights0, taa_weights, delta, risk_contribs, alphas], axis=1)
    saa_taa_portfolios = SaaTaaPortfolios(saa_valuation_date=saa_valuation_date,
                                          taa_valuation_date=taa_valuation_date,
                                          taa_df=taa_df,
                                          saa_df=saa_df,
                                          taa_covar=taa_covar,
                                          saa_covar=saa_pd_covar,
                                          universe_data=universe_data,
                                          taa_rolling_covar_data=taa_rolling_covar_data,
                                          saa_current_covar_data=saa_current_covar_data)
    return saa_taa_portfolios
