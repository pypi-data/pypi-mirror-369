"""
figures for MAS optimisation paper
"""
import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict, List
from enum import Enum
import scipy.cluster.hierarchy as spc

from optimalportfolios import (LassoModelType, LassoModel,
                               estimate_lasso_covar_different_freq,
                               estimate_rolling_lasso_covar_different_freq)

# universe data
from mac_portfolio_optimizer import (load_mac_portfolio_universe, SaaPortfolio, TaaPortfolio,
                                     MacUniverseData, RiskModel)


def plot_clusters_from_prices(prices: pd.DataFrame,
                              span: int = 24,
                              freq: str = 'QE',
                              ax: plt.Subplot = None
                              ) -> pd.Series:
    returns = qis.to_returns(prices=prices, is_log_returns=True, drop_first=True, freq=freq)
    # corr = qis.compute_masked_covar_corr(data=returns)
    a = returns - qis.compute_ewm(returns, span=span)
    corr = qis.compute_ewm_covar(a=a.to_numpy(), span=span, is_corr=True)

    pdist = spc.distance.pdist(1.0 - corr)
    linkage = spc.linkage(pdist, method='ward')
    spc.dendrogram(linkage, labels=prices.columns.to_list(), orientation="right", color_threshold=0.5 * np.max(pdist),
                   ax=ax)
    idx = spc.fcluster(linkage, 0.5 * np.max(pdist), 'distance')
    clusters = pd.Series(idx, index=prices.columns)
    clusters = clusters.sort_values(ascending=False)
    return clusters


def plot_lasso_betas_with_clusters(universe_data: MacUniverseData,
                                   lasso_model: LassoModel,
                                   risk_factor_prices:pd.DataFrame,
                                   prices: pd.DataFrame,
                                   returns_freqs: pd.Series
                                   ) -> Tuple[plt.Figure, plt.Figure]:

    if lasso_model.model_type != LassoModelType.GROUP_LASSO_CLUSTERS:
        raise ValueError(f"clusters implemented only for LassoModelType.GROUP_LASSO_CLUSTERS")

    covar_data = estimate_lasso_covar_different_freq(risk_factor_prices=risk_factor_prices,
                                                     prices=prices,
                                                     returns_freqs=returns_freqs,
                                                     lasso_model=lasso_model,
                                                     factor_returns_freq='ME',
                                                     span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                                     )

    agg_clusters, clusters_fig = plot_monthly_quarterly_clusters(clusters=covar_data.clusters,
                                                                 linkages=covar_data.linkages,
                                                                 cutoffs=covar_data.cutoffs)

    betas = covar_data.asset_last_betas.T.loc[agg_clusters.index, :]
    betas = betas.where(np.abs(betas) > 1e-6, other=np.nan)
    hline_rows = qis.get_table_lines_for_group_data(agg_clusters)
    kwargs = dict(var_format='{:.2f}', hline_rows=hline_rows)
    fig_betas, ax = plt.subplots(1, 1, figsize=(5, 10), tight_layout=True)
    qis.plot_heatmap(df=betas, ax=ax, **kwargs)

    return clusters_fig, fig_betas


def plot_lasso_betas_table(universe_data: MacUniverseData,
                           time_period: qis.TimePeriod,
                           span: int = 36
                           ) -> Tuple[plt.Figure, plt.Figure]:

    # implemented models
    lasso_models = {'(A) Multivariate Regression': LassoModel(model_type=LassoModelType.LASSO,
                                                              group_data=None, demean=True,
                                                              reg_lambda=0.0,  # 1e-5
                                                              span=span, solver='ECOS_BB'),
                    '(B) Independent Lasso': LassoModel(model_type=LassoModelType.LASSO,
                                                        group_data=None, demean=True,
                                                        reg_lambda=1e-5,
                                                        span=span, solver='ECOS_BB'),
                    '(C) Hierarchical Group Lasso': LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                                                               group_data=None, demean=True,
                                                               reg_lambda=1e-5,  # 1e-5
                                                               span=span,
                                                               solver='ECOS_BB',
                                                               nonneg=True),
                    }

    betas = {}
    add_star_to_saa_names = True
    for key, lasso_model in lasso_models.items():
        risk_factor_prices = universe_data.get_risk_factors(time_period=time_period)
        covar_data = estimate_lasso_covar_different_freq(risk_factor_prices=risk_factor_prices,
                                                         prices=universe_data.get_joint_prices(add_star_to_saa_names=add_star_to_saa_names,
                                                                                               time_period=time_period),
                                                         returns_freqs=universe_data.get_joint_rebalancing_freqs(add_star_to_saa_names=add_star_to_saa_names),
                                                         lasso_model=lasso_model,
                                                         factor_returns_freq='ME',
                                                         span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4})
        betas_hgl = covar_data.asset_last_betas
        betas[key] = betas_hgl.where(np.abs(betas_hgl) > 1e-4, other=np.nan)

    # compute clusters using last model
    agg_clusters, fig_clusters = plot_monthly_quarterly_clusters(clusters=covar_data.clusters,
                                                                 linkages=covar_data.linkages,
                                                                 cutoffs=covar_data.cutoffs)
    print(agg_clusters)

    # figure for betas
    fig_betas, axs = plt.subplots(1, len(betas.keys()), figsize=(14, 10), tight_layout=True)
    hline_rows = qis.get_table_lines_for_group_data(agg_clusters)
    kwargs = dict(var_format='{:.2f}', hline_rows=hline_rows)
    for idx, (key, beta) in enumerate(betas.items()):
        df = beta.T.loc[agg_clusters.index, :]
        qis.plot_heatmap(df=df, title=key, ax=axs[idx], **kwargs)
    return fig_betas, fig_clusters


def plot_monthly_quarterly_clusters(clusters: Dict[str, pd.Series],
                                    linkages: Dict[str, np.ndarray],
                                    cutoffs: Dict[str, float]
                                    ) -> Tuple[pd.Series, plt.Figure]:
    fig = plt.figure(figsize=(12, 10), constrained_layout=True)
    gs = fig.add_gridspec(nrows=4, ncols=3, wspace=0.0, hspace=0.0)
    axs = [fig.add_subplot(gs[0, :2]), fig.add_subplot(gs[1:, :2]), ]
    titles = [f"(A) Quarterly", f"(B) Monthly"]
    # reverse
    linkages = dict(reversed(linkages.items()))
    agg_clusters = []
    for idx, (freq, linkage) in enumerate(linkages.items()):
        ax = axs[idx]
        spc.dendrogram(linkage, labels=clusters[freq].index.to_list(), orientation="right",
                       color_threshold=cutoffs[freq],
                       ax=ax)
        qis.set_title(ax, title=titles[idx])
        ax.axvline(cutoffs[freq], color='k')
        ax.tick_params(axis='x', labelbottom=False)
        ax.tick_params(axis='y', which='major', labelsize=10)

        cluster_ = clusters[freq]
        agg_clusters.append(cluster_.apply(lambda x: f"{freq}-{x}"))
    agg_clusters = pd.concat(agg_clusters).sort_values()
    # index by inverse of agg clusters
    agg_clusters = agg_clusters.reindex(index=agg_clusters.index[::-1])

    # plot clusters
    ax = fig.add_subplot(gs[:, 2])
    qis.plot_df_table(df=agg_clusters.to_frame(name='Cluster ID'),
                      index_column_name='Instrument',
                      fontsize=10,
                      title='(C) Cluster IDs',
                      rows_edge_lines=qis.get_table_lines_for_group_data(agg_clusters),
                      ax=ax)

    return agg_clusters, fig


def plot_nw_ratios(risk_factor_prices: pd.DataFrame,
                   prices: pd.DataFrame,
                   returns_freqs: pd.Series,
                   lasso_model: LassoModel,
                   time_period: qis.TimePeriod,
                   assets: List[str] = None
                   ) -> Tuple[pd.DataFrame, plt.Figure]:

    covar_data = estimate_rolling_lasso_covar_different_freq(risk_factor_prices=risk_factor_prices,
                                                             prices=prices,
                                                             returns_freqs=returns_freqs,
                                                             time_period=time_period,
                                                             lasso_model=lasso_model,
                                                             factor_returns_freq='ME',
                                                             rebalancing_freq='ME',
                                                             span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                                             num_lags_newey_west_dict={'ME': 0, 'QE': 2})
    last_nw_ratios_pd = covar_data.last_nw_ratios_pd
    #last_nw_ratios_pd = last_nw_ratios_pd.rolling(12).mean().dropna()
    if assets is None:
        assets = returns_freqs.loc[returns_freqs == 'QE'].index.to_list()

    saa_last_nw_ratios_pd = np.sqrt(last_nw_ratios_pd[assets])
    print(saa_last_nw_ratios_pd)
    kwargs = dict(fontsize=12, framealpha=0.9)
    title = 'Newey-West adjustment ratios'
    with sns.axes_style('darkgrid'):
        fig, ax = plt.subplots(1, 1, figsize=(12, 8), tight_layout=True)
        qis.plot_time_series(df=saa_last_nw_ratios_pd,
                             title=title,
                             ax=ax,
                             **kwargs)
    return saa_last_nw_ratios_pd, fig


def plot_universe_perf(universe_data: MacUniverseData,
                       time_period: qis.TimePeriod = None,
                       is_saa: bool = True,
                       add_adjustments: bool = True
                       ) -> plt.Figure:

    if is_saa:
        prices = universe_data.get_saa_prices(time_period=time_period)
    else:
        prices = universe_data.get_taa_prices(time_period=time_period)
    benchmark_price = universe_data.compute_static_weight_saa_benchmark()
    prices = pd.concat([benchmark_price, prices], axis=1)

    if add_adjustments:
        x_var_multiplicative_adjustment = pd.Series({'Hedge Funds': 1.3,
                                                     'Private Equity': 1.45,
                                                     'Private Debt': 1.25,
                                                     'Insurance-Linked': 1.20}).reindex(index=prices.columns).fillna(1.0)
        y_var_multiplicative_adjustment1 = None
        y_var_multiplicative_adjustment2 = 1.0 / x_var_multiplicative_adjustment  # shrink sharpe
    else:
        x_var_multiplicative_adjustment = None
        y_var_multiplicative_adjustment1 = None
        y_var_multiplicative_adjustment2 = None
    print(x_var_multiplicative_adjustment)
    print(y_var_multiplicative_adjustment2)

    kwargs = dict(perf_params=qis.PerfParams(freq='QE'),
                  drop_benchmark=False,
                  ci=95,
                  benchmark=benchmark_price.name,
                  annotation_labels=prices.columns.to_list(),
                  digits_to_show=1,
                  sharpe_digits=1, framealpha=0.9,
                  full_sample_order=1,
                  full_sample_label='Regression:')

    with sns.axes_style("darkgrid"):
        fig, axs = plt.subplots(1, 2, figsize=(12, 6), tight_layout=True)
        qis.plot_ra_perf_scatter(prices=prices,
                                 x_var=qis.PerfStat.VOL,
                                 y_var=qis.PerfStat.PA_RETURN,
                                 title=f"Total return vs Vol",
                                 x_var_multiplicative_adjustment=x_var_multiplicative_adjustment,
                                 y_var_multiplicative_adjustment=y_var_multiplicative_adjustment1,
                                 ax=axs[0],
                                 **kwargs)
        qis.plot_ra_perf_scatter(prices=prices,
                                 x_var=qis.PerfStat.BETA,
                                 y_var=qis.PerfStat.SHARPE_RF0,
                                 title=f"Total Sharpe vs Beta to Equal Within-AC Weight Benchmark",
                                 x_var_multiplicative_adjustment=x_var_multiplicative_adjustment,
                                 y_var_multiplicative_adjustment=y_var_multiplicative_adjustment2,
                                 ax=axs[1],
                                 **kwargs)
    return fig


def plot_lasso_corr_matrix(universe_data: MacUniverseData,
                           lasso_model: LassoModel
                           ) -> None:

    risk_factor_prices = universe_data.get_risk_factors().loc['2010':, :]
    prices = universe_data.get_taa_prices().loc['2010':, :]
    returns_freqs = universe_data.get_joint_rebalancing_freqs()

    qis.plot_returns_corr_table(prices=prices.loc['2020':, :], freq='QE')

    covar_data = estimate_lasso_covar_different_freq(risk_factor_prices=risk_factor_prices,
                                                     prices=prices,
                                                     returns_freqs=returns_freqs,
                                                     lasso_model=lasso_model,
                                                     factor_returns_freq='ME',
                                                     rebalancing_freq='ME',
                                                     span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                                     )
    covar = covar_data.y_covar
    corrs = qis.covar_to_corr(covar=covar)
    print(corrs)
    qis.plot_heatmap(df=corrs)


class LocalTests(Enum):
    CLUSTERS = 1
    X_COVAR = 2
    LASSO_BETAS_WITH_CLUSTERS = 3
    LASSO_BETAS_TABLE = 4
    NEWEY_WEST_VOL = 5
    PLOT_INVESTMENT_UNIVERSE = 6
    PLOT_LASSO_CORR_MATRIX = 7


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
    local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
    # local_path_out = lp.get_output_path()

    lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                             group_data=None,
                             demean=True,
                             reg_lambda=1e-5,  # 2.5*1e-5
                             span=36,
                             solver='ECOS_BB',
                             warmup_period=None)

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

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')

    if local_test == LocalTests.CLUSTERS:
        fig, ax = plt.subplots(1, 1, figsize=(12, 12), tight_layout=True)
        clusters = plot_clusters_from_prices(prices=universe_data.taa_prices, ax=ax)
        print(clusters)
        # qis.save_fig(fig, file_name='clusters', local_path=local_path_out)

    elif local_test == LocalTests.X_COVAR:
        from optimalportfolios import CovarEstimator
        covar_estimator = CovarEstimator(factor_returns_freq='ME', rebalancing_freq='ME', span=36)
        covar_dict = covar_estimator.fit_rolling_covars(prices=universe_data.get_risk_factors(),
                                                       time_period=time_period).x_covars
        # pd_covar = covar_dict[list(covar_dict.keys())[-1]]
        # print(covar_dict.keys())
        dates = ['31Dec2015', '31Dec2020', '31Dec2024']
        fig, axs = plt.subplots(1, len(dates), figsize=(14, 4), tight_layout=True)
        kwargs = dict(var_format='{:.2f}')
        for idx, date in enumerate(dates):
            last_update_date = qis.find_upto_date_from_datetime_index(index=list(covar_dict.keys()), date=pd.Timestamp(date))
            pd_covar = covar_dict[last_update_date]
            norm_to_corr = 1.0/np.sqrt(np.diag(pd_covar.to_numpy()))
            pd_corr = pd_covar*np.outer(norm_to_corr, norm_to_corr)
            qis.plot_heatmap(df=pd_corr,
                             title=f"({qis.idx_to_alphabet(idx=idx+1)}) {date}",
                             ax=axs[idx], **kwargs)

        qis.save_fig(fig, file_name='x_covar', local_path=local_path_out)

    elif local_test == LocalTests.LASSO_BETAS_WITH_CLUSTERS:
        add_star_to_saa_names = False
        anonymise_taa_names = False

        risk_factor_prices = universe_data.get_risk_factors()
        prices = universe_data.get_joint_prices(add_star_to_saa_names=add_star_to_saa_names,
                                                anonymise_taa_names=anonymise_taa_names)
        returns_freqs = universe_data.get_joint_rebalancing_freqs(add_star_to_saa_names=add_star_to_saa_names,
                                                                  anonymise_taa_names=anonymise_taa_names)
        clusters_fig, fig_betas = plot_lasso_betas_with_clusters(universe_data=universe_data,
                                                                 lasso_model=lasso_model,
                                                                 risk_factor_prices=risk_factor_prices,
                                                                 prices=prices,
                                                                 returns_freqs=returns_freqs)
        #qis.save_fig(clusters_fig, file_name='clusters_fig', local_path=local_path_out)
        #qis.save_fig(fig_betas, file_name='fig_betas', local_path=local_path_out)

    elif local_test == LocalTests.LASSO_BETAS_TABLE:
        time_period = qis.TimePeriod('31Dec2004', '31Dec2024')
        fig_betas, fig_clusters = plot_lasso_betas_table(universe_data=universe_data, time_period=time_period)
        # qis.save_fig(fig_betas, file_name='betas', local_path=local_path_out)
        # qis.save_fig(fig_clusters, file_name='clusters', local_path=local_path_out)

    elif local_test == LocalTests.NEWEY_WEST_VOL:
        time_period = qis.TimePeriod('31Dec2003', '31Mar2025')
        add_star_to_saa_names = False
        anonymise_taa_names = False
        risk_factor_prices = universe_data.get_risk_factors()
        prices = universe_data.get_joint_prices(add_star_to_saa_names=add_star_to_saa_names,
                                                anonymise_taa_names=anonymise_taa_names)
        returns_freqs = universe_data.get_joint_rebalancing_freqs(add_star_to_saa_names=add_star_to_saa_names,
                                                                  anonymise_taa_names=anonymise_taa_names)
        print(prices.columns)
        assets = ['Private Equity', 'Private Debt']
        df, fig = plot_nw_ratios(risk_factor_prices=risk_factor_prices,
                                 prices=prices,
                                 lasso_model=lasso_model,
                                 returns_freqs=returns_freqs,
                                 time_period=time_period,
                                 assets=assets)
        # qis.save_fig(fig, file_name='newey_west_ratio', local_path=local_path_out)
        # qis.save_df_to_excel(data=df, file_name='newey_west_ratio', local_path=local_path_out)
        qis.save_fig(fig, file_name='newey_west_ratio2', local_path=local_path_out)

    elif local_test == LocalTests.PLOT_INVESTMENT_UNIVERSE:
        is_saa = True
        fig = plot_universe_perf(universe_data=universe_data, time_period=time_period, is_saa=is_saa)
        if is_saa:
            file_name = 'saa_universe_scatter'
        else:
            file_name = 'taa_universe_scatter'
        qis.save_fig(fig, file_name=file_name, local_path=local_path_out)

    elif local_test == LocalTests.PLOT_LASSO_CORR_MATRIX:
        plot_lasso_corr_matrix(universe_data=universe_data, lasso_model=lasso_model)
        #qis.save_fig(clusters_fig, file_name='lasso_corr', local_path=local_path_out)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.LASSO_BETAS_TABLE)
