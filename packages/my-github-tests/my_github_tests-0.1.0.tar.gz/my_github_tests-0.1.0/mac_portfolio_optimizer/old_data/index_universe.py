"""
create universe for MAS optimisation
"""
import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
from enum import Enum
from bbg_fetch import fetch_field_timeseries_per_tickers

from optimalportfolios import GroupLowerUpperConstraints, Constraints
from mac_portfolio_optimizer.old_data.universe import (UniverseData, BENCHMARK, BENCHMARK_WEIGHT, SAA_BENCHMARK_BUDGET,
                                                       INCLUDED_FOR_SAA, INCLUDED_FOR_TAA, BENCHMARK_CONSTITUENTS,
                                                       SAA_MIN, SAA_MAX, TAA_MIN, TAA_MAX, REBALANCING, ASSET_CLASS,
                                                       BENCHMARK_STATIC_WEIGHT, GIM_NAME)


def load_universe_sheet_data(local_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    select df where index is integer
    """
    df = qis.load_df_from_excel(file_name='Reference Indices for SAA Optmizations', sheet_name='SAA Detail', local_path=local_path)
    df0 = df.iloc[2:, :]
    df0.columns = df.iloc[1, :].to_list()
    # select int type
    universe_sheet_data = df0.loc[[type(x) == int for x in df0.index], :]
    # select str types 'A', 'B'
    ac_sheet_data = df0.loc[[type(x) == str for x in df0.index], :]
    ac_sheet_data = ac_sheet_data.drop(['\xa0'], axis=0)

    return universe_sheet_data, ac_sheet_data


def load_alt_sheet_data(local_path: str) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name='Reference Indices for SAA Optmizations', sheet_name='Alternative Asset Class', local_path=local_path)
    df0 = df.iloc[24:, :]
    df0.columns = df.iloc[21, :].to_list()
    with pd.option_context('future.no_silent_downcasting', True):
        df0 = df0.replace({'\xa0': np.nan}).dropna(how='all', axis=1).dropna(how='all', axis=0)  # drop ll empty columns
    # set date index
    df0 = df0.reset_index(drop=True).set_index('Backup Ticker Name in Reference Indices for SAA Optmizations.xlsx', drop=True)
    df0.index = pd.to_datetime(df0.index)
    df0.index.name = 'Date'
    df0 = df0.dropna(how='all', axis=0).astype(float)

    # pivot_returns = df0.iloc[:, 0]
    returns = {}
    df0 = df0.iloc[:, ~df0.columns.duplicated()]
    for column in df0.iloc[:, 1:].columns:
        if not column == '':
            returns[column] = df0[column].dropna()
    """
    for column in df0.iloc[:, 1:].columns:
        infrequent_returns = qis.drop_first_nan_data(df=df0[column])
        if np.any(np.isnan(infrequent_returns.iloc[:20])):
            ds = qis.interpolate_infrequent_returns(infrequent_returns=infrequent_returns.dropna(),
                                                    pivot_returns=pivot_returns,
                                                    span=12,
                                                    vol_adjustment=1.15)
        else:
            ds = infrequent_returns
        returns[column] = ds
    """
    returns = pd.DataFrame.from_dict(returns, orient='columns').fillna(0.0)
    # returns = pd.concat([pivot_returns, returns], axis=1).fillna(0.0)
    navs = qis.returns_to_nav(returns).ffill()
    return navs


def load_gim(local_path: str) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name='Reference Indices for SAA Optmizations', sheet_name='gim', local_path=local_path)
    df.index = pd.to_datetime(df.index)
    returns = df.iloc[:, 0].to_frame(GIM_NAME)
    nav = qis.returns_to_nav(returns=returns).asfreq(freq='ME', method='ffill').ffill()
    return nav


def create_index_universe_data_from_sheet(universe_df: pd.DataFrame,
                                          alt_prices: pd.DataFrame,
                                          ac_df: pd.DataFrame,
                                          start_date: pd.Timestamp = pd.Timestamp('31Dec1999'),
                                          update_prices: bool = True,
                                          local_path: str = None
                                          ) -> Dict[str, pd.DataFrame]:

    # filter out assets with zero FactorWeight AssetBudgetWeight
    # cond0 = np.isclose(universe_df['Included'].astype(float), 0.0)
    included_for_saa = universe_df[INCLUDED_FOR_SAA] == 'Yes'
    included_for_taa = universe_df[INCLUDED_FOR_TAA] == 'Yes'
    cond0 = np.logical_or(included_for_saa, included_for_taa)
    universe_df = universe_df.loc[cond0, :]

    # 1. fetch bbg data
    # remove dublicate data source
    universe_df = universe_df.loc[:, ~universe_df.columns.duplicated(keep='first')]
    cond1 = universe_df['Data Source'] == 'Bloomberg'  # take the first one
    primary_tickers = universe_df.loc[cond1, 'Primary Ticker'].apply(lambda x: f"{x} Index")
    backup_tickers = universe_df.loc[cond1, 'Backup Ticker ']\
        .replace({'---': np.nan, '\xa0': np.nan, ' ': np.nan}).dropna().apply(lambda x: f"{x} Index")
    universe_df = pd.concat([universe_df, primary_tickers.rename('tickers1'), backup_tickers.rename('tickers2')], axis=1)
    universe_df = universe_df.astype({"tickers1": str, "tickers2": str})
    with pd.option_context('future.no_silent_downcasting', True):
        universe_df = universe_df.replace({'\xa0': np.nan})
    universe_df = universe_df.dropna(axis=1, how='all')  # frop empty columns
    universe_df = universe_df.reset_index(drop=True).set_index('AssetName')

    if update_prices:
        primary_prices = fetch_field_timeseries_per_tickers(tickers=primary_tickers.to_list(), freq='B', start_date=start_date)
        backup_prices = fetch_field_timeseries_per_tickers(tickers=backup_tickers.to_list(), freq='B', start_date=start_date)

        # 2. generate asset prices
        asset_prices = {}
        for name, row in universe_df.to_dict(orient='index').items():  # row is dict of columns values
            source = row['Data Source']
            if source == 'Bloomberg':
                if not pd.isna(row['tickers2']) and not row['tickers2'] == 'nan':
                    asset_prices[name] = qis.bfill_timeseries(df_newer=primary_prices[row['tickers1']], df_older=backup_prices[row['tickers2']], is_prices=True)
                else:
                    asset_prices[name] = primary_prices[row['tickers1']]
            elif source == 'MSCI - Pending':
                ticker = row['Backup Ticker Name']
                asset_prices[name] = alt_prices[ticker]
        asset_prices = pd.DataFrame.from_dict(asset_prices, orient='columns').asfreq('ME', method='ffill').ffill()

        # 3 construct benchmarks
        saa_benchmark_prices = {}
        saa_benchmark_budgets = {}
        benchmark_min = {}
        benchmark_max = {}
        benchmark_constituents = {}
        benchmark_ac = {}
        benchmark_rebalancing = {}
        benchmark_equal_weight = {}
        universe_df[SAA_BENCHMARK_BUDGET] = universe_df[SAA_BENCHMARK_BUDGET].astype(float)
        for benchmark, df in universe_df.groupby(BENCHMARK, dropna=True, sort=False):
            saa_benchmark_budgets[benchmark] = df[SAA_BENCHMARK_BUDGET].iloc[0]
            benchmark_min[benchmark] = df[SAA_MIN].iloc[0]
            benchmark_max[benchmark] = df[SAA_MAX].iloc[0]
            benchmark_constituents[benchmark] = df[BENCHMARK_CONSTITUENTS].iloc[0]
            benchmark_ac[benchmark] = df[ASSET_CLASS].iloc[0]
            benchmark_equal_weight[benchmark] = df[BENCHMARK_STATIC_WEIGHT].iloc[0]
            benchmark_rebalancing[benchmark] = df[REBALANCING].iloc[0]
            if len(df.index) == 1 or np.isclose(df[BENCHMARK_WEIGHT].iloc[0], 1.0):
                saa_benchmark_prices[benchmark] = asset_prices[df.index[0]]
            else:
                saa_benchmark_prices[benchmark] = qis.backtest_model_portfolio(prices=asset_prices[df.index],
                                                                               weights=df[BENCHMARK_WEIGHT],
                                                                               rebalancing_freq='QE').get_portfolio_nav()
        saa_benchmark_prices = pd.DataFrame.from_dict(saa_benchmark_prices, orient='columns').asfreq('ME', method='ffill').ffill()
        saa_benchmark_budgets = pd.concat([pd.Series(saa_benchmark_budgets, name=SAA_BENCHMARK_BUDGET),
                                           pd.Series(benchmark_min, name=SAA_MIN),
                                           pd.Series(benchmark_max, name=SAA_MAX),
                                           pd.Series(benchmark_constituents, name=BENCHMARK_CONSTITUENTS),
                                           pd.Series(benchmark_ac, name=ASSET_CLASS),
                                           pd.Series(benchmark_rebalancing, name=REBALANCING),
                                           pd.Series(benchmark_equal_weight, name=BENCHMARK_STATIC_WEIGHT)
                                           ], axis=1)

    else:
        data = load_index_universe_datasets(local_path=local_path)
        asset_prices = data['asset_prices']
        saa_benchmark_prices = data['saa_benchmark_prices']
        saa_benchmark_budgets = data['saa_benchmark_budgets']

    # 4. create ac loadings
    ac_df = ac_df.reset_index().set_index('Primary Asset Class')[[SAA_MIN, SAA_MAX]]
    ac_loadings = qis.set_group_loadings(group_data=universe_df['Asset Class'], group_order=ac_df.index.to_list())
    ac_loadings = ac_loadings.loc[asset_prices.columns, :]  # align

    # 5. benchmarks data
    benchmarks = load_gim(local_path=local_path)

    data = dict(asset_prices=asset_prices,
                saa_benchmark_prices=saa_benchmark_prices,
                descriptive_df=universe_df,
                saa_benchmark_budgets=saa_benchmark_budgets,
                ac_loadings=ac_loadings,
                ac_df=ac_df,
                benchmarks=benchmarks)
    return data


def load_index_universe_datasets(local_path: str) -> Dict[str, pd.DataFrame]:
    dataset_keys = ['asset_prices', 'saa_benchmark_prices', 'descriptive_df', 'saa_benchmark_budgets', 'ac_loadings', 'ac_df', 'benchmarks']
    data = qis.load_df_dict_from_csv(dataset_keys=dataset_keys, file_name='index', local_path=local_path)
    return data


def load_index_universe_data(local_path: str,
                             add_max_ac_constraints: bool = False,
                             included_risk_factors: List[str] = ['Credit', 'Rates', 'HY Credit', 'EM bonds', 'Equity', 'Hedge Fund', 'Real Assets']
                             ) -> UniverseData:
    data = load_index_universe_datasets(local_path=local_path)
    saa_prices = data['saa_benchmark_prices'].dropna()
    taa_prices = data['asset_prices'].reindex(index=saa_prices.index, method='ffill')

    saa_benchmark_budgets_df = data['saa_benchmark_budgets']
    descriptive_df = data['descriptive_df']
    benchmarks = data['benchmarks']

    # extended universe with saa_benchmark_prices and asset_prices
    joint_assets = qis.merge_lists_unique(saa_prices.columns, taa_prices.columns)
    joint_prices = pd.concat([saa_prices, taa_prices], axis=1)
    joint_prices = joint_prices.loc[:, ~joint_prices.columns.duplicated(keep='first')]
    joint_prices = joint_prices[joint_assets]  # arrange

    # ac
    saa_group_data = saa_benchmark_budgets_df[ASSET_CLASS]
    asset_ac = descriptive_df.loc[taa_prices.columns, ASSET_CLASS]
    joint_ac = pd.concat([saa_group_data, asset_ac])
    joint_ac = joint_ac[~joint_ac.index.duplicated()][joint_assets]

    # constraints
    # create weights = benchmark budget * AssetBudgetWeight
    #factor_weights = descriptive_df[BENCHMARK_WEIGHT].replace({0.8: 1.0, 0.2: 0.0})
    #asset_groups = descriptive_df[BENCHMARK]
    #assets_budgets = asset_groups.map(saa_benchmark_budgets) * factor_weights
    #assets_budgets = assets_budgets[joint_prices.columns]

    # create constraints and ac constraints
    ac_df = data['ac_df']
    saa_loadings = qis.set_group_loadings(group_data=saa_group_data)
    if add_max_ac_constraints:
        saa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=saa_loadings,
                                                                       group_min_allocation=None,
                                                                       group_max_allocation=ac_df[SAA_MAX])
    else:
        saa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=saa_loadings,
                                                                       group_min_allocation=ac_df[SAA_MIN],
                                                                       group_max_allocation=ac_df[SAA_MAX])
    taa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=qis.set_group_loadings(group_data=joint_ac),
                                                                   group_min_allocation=ac_df[SAA_MIN],
                                                                   group_max_allocation=ac_df[SAA_MAX])
    # make sure we do not allocate to asset with zero budgets
    #saa_min_weights = descriptive_df.loc[prices.columns, 'SAA Min']  # pd.Series(0.0, index=prices.columns)
    #saa_max_weights = descriptive_df.loc[prices.columns, 'SAA Max']  # pd.Series(1.0, index=prices.columns)
    #saa_min_weights[np.isclose(assets_budgets, 0.0)] = 0.0
    #saa_max_weights[np.isclose(assets_budgets, 0.0)] = 0.0

    # create saa min weights
    #benchmark_mins = saa_benchmark_budgets_df.loc[:, SAA_MIN]
    #benchmark_maxs = saa_benchmark_budgets_df.loc[:, SAA_MAX]
    #saa_min_weights = asset_groups.map(benchmark_mins) * factor_weights
    #saa_max_weights = asset_groups.map(benchmark_maxs) * factor_weights
    saa_constraints = Constraints(min_weights=saa_benchmark_budgets_df.loc[:, SAA_MIN],
                                  max_weights=saa_benchmark_budgets_df.loc[:, SAA_MAX],
                                  group_lower_upper_constraints=saa_group_lower_upper_constraints,
                                  apply_total_to_good_ratio_for_constraints=False)

    with pd.option_context('future.no_silent_downcasting', True):
        taa_min_weights = descriptive_df.loc[taa_prices.columns, TAA_MIN].reindex(index=joint_assets).fillna(0.0)
        taa_max_weights = descriptive_df.loc[taa_prices.columns, TAA_MAX].reindex(index=joint_assets).fillna(0.0)

    taa_constraints = Constraints(min_weights=taa_min_weights,
                                  max_weights=taa_max_weights,
                                  group_lower_upper_constraints=taa_group_lower_upper_constraints,
                                  apply_total_to_good_ratio_for_constraints=False)
    """
    taa_constraints = Constraints(min_weights=pd.Series(0.0, index=prices.columns),
                                  max_weights=descriptive_df.loc[prices.columns, 'TAA Max'], #pd.Series(1.0, index=prices.columns),
                                  group_lower_upper_constraints=group_lower_upper_constraints,
                                  apply_total_to_good_ratio_for_constraints=False)
    """
    # print(f"benchmark_budgets={benchmark_budgets}")
    # print(f"assets_budgets=\n{assets_budgets}")
    # print(group_lower_upper_constraints)

    # group data for reporting
    group_data_sub_ac = pd.concat([pd.Series(saa_benchmark_budgets_df.index, index=saa_benchmark_budgets_df.index),
                            descriptive_df.loc[taa_prices.columns, BENCHMARK]])
    group_data_sub_ac = group_data_sub_ac[~group_data_sub_ac.index.duplicated()][joint_assets]

    group_order_sub_ac = ['Rates', 'HY Credit', 'EM bonds', 'Others FI',
                          'Equity',
                          'Hedge Fund', 'Private Assets', 'Private Debt',
                          'Real Assets', 'Insurance-Linked', 'Liquidity']

    saa_rebalancing_freqs = pd.Series('QE', index=saa_benchmark_budgets_df.index)
    rebalancing_freqs = descriptive_df.loc[taa_prices.columns, REBALANCING]
    rebalancing_freqs = pd.concat([saa_rebalancing_freqs, rebalancing_freqs])
    rebalancing_freqs = rebalancing_freqs[~rebalancing_freqs.index.duplicated()][joint_prices.columns]

    risk_factor_prices = saa_prices[included_risk_factors]
    universe_data = UniverseData(saa_prices=saa_prices,  # nb can be restructured
                                 taa_prices=taa_prices,
                                 joint_prices=joint_prices,
                                 risk_factors_prices=risk_factor_prices,
                                 benchmarks=benchmarks,
                                 saa_benchmark_budgets_df=saa_benchmark_budgets_df,
                                 saa_assets_budgets=saa_benchmark_budgets_df.loc[:, SAA_BENCHMARK_BUDGET],
                                 saa_constraints=saa_constraints,
                                 taa_constraints=taa_constraints,
                                 rebalancing_freqs=rebalancing_freqs,
                                 group_data_sub_ac=group_data_sub_ac,
                                 group_order_sub_ac=group_order_sub_ac,
                                 group_data=joint_ac,
                                 group_order=['Fixed Income', 'Equity', 'Alternatives'],
                                 descriptive_df=descriptive_df)
    return universe_data


class LocalTests(Enum):
    CHECK = 1
    CREATE_UNIVERSE_DATA = 2
    REPORT_UNIVERSE = 3
    GIM_PERFORMANCE = 4
    LOAD = 5


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
    local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//"

    if local_test == LocalTests.CHECK:
        pass
        """
        alt_prices = load_alt_sheet_data(local_path=local_path)
        print(alt_prices)

        fig = plt.figure(figsize=(12, 10), constrained_layout=True)
        gs = fig.add_gridspec(nrows=3, ncols=2, wspace=0.0, hspace=0.0)
        qis.plot_ra_perf_table(prices=alt_prices, perf_params=qis.PerfParams(freq='ME'), title='Monthly Sampling', ax=fig.add_subplot(gs[0, :]))
        qis.plot_ra_perf_table(prices=alt_prices, perf_params=qis.PerfParams(freq='QE'), title='Quarterly Sampling', ax=fig.add_subplot(gs[1, :]))
        qis.plot_returns_corr_table(prices=alt_prices, freq='ME', title='Monthly Sampling', ax=fig.add_subplot(gs[2, 0]))
        qis.plot_returns_corr_table(prices=alt_prices, freq='QE', title='Quarterly Sampling', ax=fig.add_subplot(gs[2, 1]))
        """

    elif local_test == LocalTests.CREATE_UNIVERSE_DATA:
        universe_df, ac_df = load_universe_sheet_data(local_path=local_path)
        alt_prices = load_alt_sheet_data(local_path=local_path)
        print(alt_prices)
        data = create_index_universe_data_from_sheet(universe_df=universe_df, alt_prices=alt_prices, ac_df=ac_df,
                                                     update_prices=True,
                                                     local_path=local_path)
        qis.save_df_dict_to_csv(data, file_name='index', local_path=local_path)

    elif local_test == LocalTests.REPORT_UNIVERSE:
        data = load_index_universe_datasets(local_path=local_path)
        benchmark_prices = data['benchmark_prices'].dropna()
        prices = data['asset_prices'].reindex(index=benchmark_prices.index, method='ffill')

        perf_params = qis.PerfParams(freq='QE', freq_reg='QE', alpha_an_factor=4, rates_data=None)
        qis.plot_ra_perf_table(prices=benchmark_prices, perf_params=perf_params)
        qis.plot_ra_perf_table(prices=prices, perf_params=perf_params)

        returns = qis.to_returns(prices=prices, freq='QE')
        vols = qis.compute_ewm_vol(data=returns, span=12, annualization_factor=4)
        qis.plot_time_series(vols, var_format='{:,.2%}', framealpha=0.9)
        qis.plot_returns_corr_table(prices=prices, freq='QE')

    elif local_test == LocalTests.GIM_PERFORMANCE:
        perf_params = qis.PerfParams(freq='QE', freq_reg='QE', alpha_an_factor=4, rates_data=None)
        universe_data = load_index_universe_data(local_path=local_path)
        sw = universe_data.compute_static_weight_saa_benchmark()
        benchmarks = pd.concat([universe_data.benchmarks, sw], axis=1)
        print(benchmarks)
        qis.plot_ra_perf_table_benchmark(prices=benchmarks,
                                         benchmark=GIM_NAME,
                                         perf_params=perf_params)

    elif local_test == LocalTests.LOAD:
        universe_data = load_index_universe_data(local_path=local_path)
        print(universe_data)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.CREATE_UNIVERSE_DATA)
