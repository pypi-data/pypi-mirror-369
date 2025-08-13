import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
from typing import List
from enum import Enum

from optimalportfolios import GroupLowerUpperConstraints, Constraints
from mac_portfolio_optimizer.old_data.index_universe import load_index_universe_datasets
from mac_portfolio_optimizer.old_data.universe import UniverseData, BENCHMARK, SAA_BENCHMARK_BUDGET, \
    SAA_MIN, SAA_MAX, TAA_MIN, TAA_MAX, REBALANCING, ASSET_CLASS


def load_funds_universe_sheet_data(local_path: str) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name='MAC Allocation Tracker v.2', sheet_name='Model Ledger', local_path=local_path)
    # first row and use zero row as columns
    df0 = df.iloc[3:, :]
    df0.columns = df.iloc[1, :]
    # skip rows without int id
    df0 = df0.loc[[type(x) == int for x in df0.index], :]
    df0 = df0.loc[df0['Ticker'] != '---', :]
    df0 = df0.rename({'Investment Vehicle Name': 'Asset'}, axis=1)
    df0 = df0[['Asset', 'Ticker', 'ISIN', 'Currency', 'asset_class', BENCHMARK, REBALANCING, TAA_MIN, TAA_MAX]]
    df0 = df0.set_index('Ticker', drop=True)
    return df0


def load_returns_data(local_path: str) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name='Return Series Database', sheet_name='Funds Track Records', local_path=local_path)
    df0 = df.iloc[26:, :]
    df0.columns = df.iloc[18, :].to_list()
    df0 = df0.reset_index(drop=True).set_index('Main Ticker', drop=True)
    with pd.option_context('future.no_silent_downcasting', True):
        df0 = df0.replace({'\xa0': np.nan}).dropna(how='all', axis=0)  # drop ll empty rows
    df0 = df0.astype(float).fillna(0.0)
    df0.index = pd.to_datetime(df0.index)
    df0 = df0.loc[:, ~df0.columns.duplicated(keep='first')]  # iwm
    return df0


def load_funds_universe_data(local_path: str,
                             add_max_ac_constraints: bool = False,
                             included_risk_factors: List[str] = ['Credit', 'Rates', 'HY Credit', 'EM bonds', 'Equity', 'Hedge Fund', 'Real Assets']
                             ) -> UniverseData:
    # for saa data
    data = load_index_universe_datasets(local_path=local_path)
    saa_prices = data['saa_benchmark_prices']
    saa_benchmark_budgets_df = data['saa_benchmark_budgets']
    ac_df = data['ac_df']

    saa_group_data = saa_benchmark_budgets_df.loc[:, ASSET_CLASS]
    saa_ac_loadings = qis.set_group_loadings(group_data=saa_group_data)
    if add_max_ac_constraints:
        saa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=saa_ac_loadings,
                                                                       group_min_allocation=None,
                                                                       group_max_allocation=ac_df[SAA_MAX])
    else:
        saa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=saa_ac_loadings,
                                                                       group_min_allocation=ac_df[SAA_MIN],
                                                                       group_max_allocation=ac_df[SAA_MAX])

    saa_constraints = Constraints(min_weights=saa_benchmark_budgets_df.loc[:, SAA_MIN],
                                  max_weights=saa_benchmark_budgets_df.loc[:, SAA_MAX],
                                  group_lower_upper_constraints=saa_group_lower_upper_constraints,
                                  apply_total_to_good_ratio_for_constraints=False)

    # for taa data prices
    descriptive_df = load_funds_universe_sheet_data(local_path=local_path)
    returns = load_returns_data(local_path=local_path)[descriptive_df.index]
    taa_prices = qis.returns_to_nav(returns=returns)
    taa_prices = taa_prices.reindex(index=saa_prices.index, method='ffill')

    # extended universe with saa_benchmark_prices and asset_prices
    joint_assets = qis.merge_lists_unique(saa_prices.columns, taa_prices.columns)
    joint_prices = pd.concat([saa_prices, taa_prices], axis=1)
    joint_prices = joint_prices.loc[:, ~joint_prices.columns.duplicated(keep='first')]
    joint_prices = joint_prices[joint_assets]  # arrange

    # ac
    asset_ac = descriptive_df.loc[taa_prices.columns, 'asset_class']
    joint_ac = pd.concat([saa_group_data, asset_ac])
    joint_ac = joint_ac[~joint_ac.index.duplicated()][joint_assets]

    # constraints
    with pd.option_context('future.no_silent_downcasting', True):
        taa_min_weights = descriptive_df.loc[taa_prices.columns, TAA_MIN].reindex(index=joint_assets).fillna(0.0)
        taa_max_weights = descriptive_df.loc[taa_prices.columns, TAA_MAX].reindex(index=joint_assets).fillna(0.0)

    taa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=qis.set_group_loadings(group_data=joint_ac),
                                                                   group_min_allocation=ac_df[SAA_MIN],
                                                                   group_max_allocation=ac_df[SAA_MAX])

    taa_constraints = Constraints(min_weights=taa_min_weights,
                                  max_weights=taa_max_weights,
                                  group_lower_upper_constraints=taa_group_lower_upper_constraints,
                                  apply_total_to_good_ratio_for_constraints=False)

    # group data for reporting
    group_data = pd.concat([pd.Series(saa_benchmark_budgets_df.index, index=saa_benchmark_budgets_df.index),
                            descriptive_df.loc[taa_prices.columns, BENCHMARK]])
    group_data = group_data[~group_data.index.duplicated()][joint_assets]

    group_order = ['Rates', 'HY Credit', 'EM bonds', 'Others FI',
                   'Equity',
                   'Hedge Fund', 'Private Assets', 'Private Debt',
                   'Real Assets', 'Insurance-Linked', 'Liquidity']

    # for saa assets
    taa_rebalancing_freqs = descriptive_df.loc[taa_prices.columns, REBALANCING]
    saa_rebalancing_freqs = saa_benchmark_budgets_df[REBALANCING] #  .reindex(index=joint_assets).fillna('ME'))
    rebalancing_freqs = pd.concat([taa_rebalancing_freqs, saa_rebalancing_freqs]).reindex(index=joint_assets)
    risk_factor_prices = saa_prices[included_risk_factors]

    universe_data = UniverseData(saa_prices=saa_prices,
                                 taa_prices=taa_prices,
                                 joint_prices=joint_prices,
                                 risk_factors_prices=risk_factor_prices,
                                 benchmarks=data['benchmarks'],
                                 saa_benchmark_budgets_df=saa_benchmark_budgets_df,
                                 saa_assets_budgets=saa_benchmark_budgets_df.loc[:, SAA_BENCHMARK_BUDGET],
                                 saa_constraints=saa_constraints,
                                 taa_constraints=taa_constraints,
                                 rebalancing_freqs=rebalancing_freqs,
                                 group_data_sub_ac=group_data,
                                 group_order_sub_ac=group_order,
                                 group_data=joint_ac,
                                 group_order=['Fixed Income', 'Equity', 'Alternatives'],
                                 descriptive_df=descriptive_df)
    return universe_data


class LocalTests(Enum):
    CHECK = 1
    LOAD = 2


def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    import quant_strats.local_path as lp
    local_path = f"{lp.get_resource_path()}regime_allocation//"

    if local_test == LocalTests.CHECK:
        desc = load_funds_universe_sheet_data(local_path=local_path)
        print(desc)
        prices = load_returns_data(local_path=local_path)
        prices1 = prices[desc.index]
        print(prices1)

    elif local_test == LocalTests.LOAD:
        universe_data = load_funds_universe_data(local_path=local_path)
        print(universe_data)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.LOAD)
