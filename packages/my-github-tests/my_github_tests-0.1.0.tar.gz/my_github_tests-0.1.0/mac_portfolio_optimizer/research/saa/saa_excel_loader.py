"""
load instance of SAA universe from WMI_Template_20250616
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import qis as qis
from typing import Tuple
from enum import Enum

from mac_portfolio_optimizer.data.excel_loader import (fetch_risk_factors_from_saa_index_paper,
                                                       load_universe_returns_from_sheet_data)
from mac_portfolio_optimizer.data.mac_universe import (UniverseColumns, MacUniverseData)
from mac_portfolio_optimizer.research.saa.saa_universe import (SaaUniverseColumns,
                                                               SAA_TO_MAC_COLUMNS_MAP, Family,
                                                               BaseCcy, RiskProfile,
                                                               AltIntType, CmaType,
                                                               SAA_AC_LEVEL1)

FEEDER_EXCEL_FILE = 'WMI_Template_20250616'
CMAS_FEEDER_EXCEL_FILE = 'CMAs'


def load_mandates_data_from_excel(local_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mandates_df = qis.load_df_from_excel(file_name=FEEDER_EXCEL_FILE, sheet_name='AssetAllocation',
                                         local_path=local_path)
    ranges_df = qis.load_df_from_excel(file_name=FEEDER_EXCEL_FILE, sheet_name='Ranges', local_path=local_path)
    return mandates_df, ranges_df


def parse_mandate_data(mandates_df: pd.DataFrame,
                       ranges_df: pd.DataFrame,
                       family: Family = Family.CLASSIC,
                       base_ccy: BaseCcy = BaseCcy.USD,
                       risk_profile: RiskProfile = RiskProfile.MODERATE,
                       alt_inv_type: AltIntType = AltIntType.AI,
                       aa_type: str = 'SAA'
                       ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cond1 = (mandates_df[SaaUniverseColumns.FAMILY] == family.value) & \
            (mandates_df[SaaUniverseColumns.BASE_CCY] == base_ccy.value) & \
            (mandates_df[SaaUniverseColumns.RISK_PROFILE] == risk_profile.value) & \
            (mandates_df[SaaUniverseColumns.ALT_INV] == alt_inv_type) & \
            (mandates_df[SaaUniverseColumns.AA_TYPE] == aa_type)
    mandate_df = mandates_df.loc[cond1, :]

    cond2 = (ranges_df[SaaUniverseColumns.FAMILY] == family.value) & \
            (ranges_df[SaaUniverseColumns.BASE_CCY] == base_ccy.value) & \
            (ranges_df[SaaUniverseColumns.RISK_PROFILE] == risk_profile.value) & \
            (ranges_df[SaaUniverseColumns.ALT_INV] == alt_inv_type)
    mandate_range = ranges_df.loc[cond2, :]

    mandate_df = mandate_df.reset_index().set_index(SaaUniverseColumns.AC_KEY.value)

    mandate_df = mandate_df.rename(SAA_TO_MAC_COLUMNS_MAP, axis=1)
    mandate_df[UniverseColumns.BENCHMARK_STATIC_WEIGHT.value] *= 0.01  # weights are given in 100%
    mandate_df[UniverseColumns.REBALANCING.value] = 'ME'
    mandate_df[UniverseColumns.TURNOVER_GROUP.value] = 1

    return mandate_df, mandate_range


def load_saa_mac_universe(local_path: str,
                          family: Family = Family.CLASSIC,
                          base_ccy: BaseCcy = BaseCcy.USD,
                          risk_profile: RiskProfile = RiskProfile.MODERATE,
                          alt_inv_type: AltIntType = AltIntType.AI,
                          cma_type: CmaType = CmaType.LGT_CMAS,
                          benchmark_underweight_ratio: float = 0.5,
                          benchmark_overweight_ratio: float = 1.5
                          ) -> MacUniverseData:
    """
    load SAA data for MacUniverseData container
    """
    mandates_df, ranges_df = load_mandates_data_from_excel(local_path=local_path)
    mandate_df, mandate_range = parse_mandate_data(mandates_df=mandates_df,
                                                   ranges_df=ranges_df,
                                                   family=family,
                                                   base_ccy=base_ccy,
                                                   risk_profile=risk_profile,
                                                   alt_inv_type=alt_inv_type)
    # add min max
    mandate_df[UniverseColumns.MIN.value] = benchmark_underweight_ratio*mandate_df[UniverseColumns.BENCHMARK_STATIC_WEIGHT.value]
    mandate_df[UniverseColumns.MAX.value] = np.minimum(benchmark_overweight_ratio*mandate_df[UniverseColumns.BENCHMARK_STATIC_WEIGHT.value], 1.0)


    # tickers = mandate_df[SaaUniverseColumns.TICKER.value].to_list()
    # prices = qis.load_df_from_csv(file_name='wmi_bbg_prices', local_path=local_path)
    cma_tickers = mandate_df.index.to_list()

    prices = load_qach_prices(local_path=local_path)
    saa_prices = prices[cma_tickers]
    # qis.plot_ra_perf_table(prices=saa_prices)

    asset_class_ranges = mandate_range[['ACLvl1', 'Lower', 'Upper']].reset_index(drop=True).set_index('ACLvl1', drop=True)
    asset_class_ranges = 0.01 * asset_class_ranges.rename({'Lower': UniverseColumns.MIN.value,
                                                           'Upper': UniverseColumns.MAX.value}, axis=1)
    print(asset_class_ranges)

    universe_returns = load_universe_returns_from_sheet_data(local_path=local_path)
    risk_factor_prices = fetch_risk_factors_from_saa_index_paper(local_path=local_path,
                                                                 universe_returns=universe_returns)
    saa_prices = saa_prices.reindex(index=risk_factor_prices.index).ffill()

    saa_universe_data = MacUniverseData(saa_prices=saa_prices,
                                        saa_universe_df=mandate_df,
                                        taa_prices=saa_prices,
                                        taa_universe_df=mandate_df,
                                        asset_class_ranges=asset_class_ranges,
                                        risk_factor_prices=risk_factor_prices,
                                        ac_group_order=SAA_AC_LEVEL1)

    mandate_weight = mandate_df[UniverseColumns.BENCHMARK_STATIC_WEIGHT.value]
    benchmark = saa_universe_data.compute_static_weight_saa_benchmark(weights=mandate_weight,
                                                                      rebalancing_freq='YE')
    saa_universe_data.benchmarks = benchmark.to_frame()

    cmas = qis.load_df_from_excel(file_name=CMAS_FEEDER_EXCEL_FILE, sheet_name=cma_type.value, local_path=local_path)
    cmas.index = pd.to_datetime(cmas.index, dayfirst=True)
    cmas = cmas.sort_index()
    saa_universe_data.cmas = cmas[cma_tickers]

    return saa_universe_data

def load_qach_prices(local_path: str) -> pd.DataFrame:
    data = qis.load_df_dict_from_excel(file_name='qach_prices', dataset_keys=['W', 'M', 'Q'], local_path=local_path)
    dfs = []
    for key, df in data.items():
        df.index = pd.to_datetime(df.index, dayfirst=True)
        dfs.append(df)
    prices = pd.concat(dfs, axis=1).sort_index()
    prices = prices.loc[:, ~prices.columns.duplicated(keep='first')]

    return prices


class LocalTests(Enum):
    SHEET_DATA = 1
    CREATE_BBG_DATA = 2
    QACH_DATA = 3
    REPORT_PRICE = 4
    MANDATE_DATA = 5
    LOAD_SAA_MAC_UNIVERSE = 6


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    from mac_portfolio_optimizer.local_path import LOCAL_PATH
    local_path = LOCAL_PATH

    if local_test == LocalTests.SHEET_DATA:
        mandates_df, ranges_df = load_mandates_data_from_excel(local_path=local_path)
        print(mandates_df)
        print(f"Family={mandates_df['Family'].unique()}")
        print(f"BaseCcy={mandates_df['BaseCcy'].unique()}")
        print(f"RiskProfile={mandates_df['RiskProfile'].unique()}")
        print(f"AltInv={mandates_df['AltInv'].unique()}")
        print(f"AAType={mandates_df['AAType'].unique()}")
        print(f"BBTickerFull={mandates_df['BBTickerFull'].unique()}")

    elif local_test == LocalTests.CREATE_BBG_DATA:
        mandates_df, ranges_df = load_mandates_data_from_excel(local_path=local_path)
        tickers = mandates_df[SaaUniverseColumns.TICKER].unique().tolist()
        print(tickers)
        print(len(tickers))
        from bbg_fetch import fetch_field_timeseries_per_tickers
        bbg_prices = fetch_field_timeseries_per_tickers(tickers=tickers, freq='B').replace(
            {0: np.nan, 0.0: np.nan}).ffill()
        qis.save_df_to_csv(df=bbg_prices, file_name='wmi_bbg_prices', local_path=local_path)

    elif local_test == LocalTests.REPORT_PRICE:
        prices = qis.load_df_from_csv(file_name='wmi_bbg_prices', local_path=local_path)
        qis.plot_ra_perf_table(prices=prices)

    elif local_test == LocalTests.QACH_DATA:
        prices = load_qach_prices(local_path=local_path)
        print(prices)
        qis.plot_ra_perf_table(prices=prices, perf_params=qis.PerfParams(freq='QE'))

    elif local_test == LocalTests.MANDATE_DATA:
        mandates_df, ranges_df = load_mandates_data_from_excel(local_path=local_path)
        mandate_df, range_df = parse_mandate_data(mandates_df=mandates_df, ranges_df=ranges_df)
        print(mandate_df)
        print(range_df)

    elif local_test == LocalTests.LOAD_SAA_MAC_UNIVERSE:
        saa_universe_data = load_saa_mac_universe(local_path=local_path)
        print(saa_universe_data)
        this = saa_universe_data.get_saa_constraints(add_max_ac_constraints=True)
        print(this)
        qis.plot_prices(saa_universe_data.benchmarks)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.LOAD_SAA_MAC_UNIVERSE)
