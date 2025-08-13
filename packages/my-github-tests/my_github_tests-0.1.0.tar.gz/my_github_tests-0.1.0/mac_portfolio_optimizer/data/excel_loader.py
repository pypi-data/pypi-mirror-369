"""
Load MacUniverseData using excel spreadsheet
"""

import pandas as pd
import numpy as np
import qis as qis
from typing import Tuple, Optional, Union, List
from enum import Enum

from mac_portfolio_optimizer.data.mac_universe import (SUB_ASSET_CLASS_DEFINITIONS,
                                                       MacUniverseData,
                                                       UniverseColumns,
                                                       RISK_FACTORS, SaaPortfolio, TaaPortfolio,
                                                       SaaRangeConstraints,
                                                       RiskModel)
import mac_portfolio_optimizer.local_path as lp

FEEDER_EXCEL_FILE = 'MAC Allocation Tracker v.5'


def load_mac_portfolio_universe(local_path: str,
                                saa_portfolio: Union[SaaPortfolio, str] = SaaPortfolio.SAA_INDEX_MAC,
                                taa_portfolio: Optional[Union[SaaPortfolio, TaaPortfolio, str]] = TaaPortfolio.TAA_FUNDS_MAC,
                                saa_range_constraints: Union[SaaRangeConstraints, str] = SaaRangeConstraints.MAC_SAA_RANGES,
                                sub_asset_class_ranges_sheet_name: Optional[str] = None,
                                risk_model: RiskModel = RiskModel.PRICE_FACTORS_FROM_MAC_PAPER,
                                file_name: str = FEEDER_EXCEL_FILE
                                ) -> MacUniverseData:
    """
    core function to fetch mac universe data
    """
    universe_returns = load_universe_returns_from_sheet_data(local_path=local_path)

    saa_prices, saa_universe_df, saa_asset_loadings = fetch_portfolio_data(local_path=local_path,
                                                                           universe_returns=universe_returns,
                                                                           portfolio=saa_portfolio,
                                                                           file_name=file_name)

    if taa_portfolio is not None:
        taa_prices, taa_universe_df, asset_loadings = fetch_portfolio_data(local_path=local_path,
                                                                           universe_returns=universe_returns,
                                                                           portfolio=taa_portfolio,
                                                                           file_name=file_name)
    else:
        taa_prices, taa_universe_df, asset_loadings = saa_prices, saa_universe_df, saa_asset_loadings

    benchmarks = qis.returns_to_nav(universe_returns['LGPSUSB LE']).to_frame('LGT PS GIM USD B')

    if isinstance(saa_range_constraints, SaaRangeConstraints):  # enumerators
        saa_range_constraints = saa_range_constraints.value

    asset_class_ranges = load_asset_class_ranges(local_path=local_path,
                                                 sheet_name=saa_range_constraints,
                                                 file_name=file_name)

    if sub_asset_class_ranges_sheet_name is not None:
        sub_asset_class_ranges = load_sub_asset_class_ranges(local_path=local_path,
                                                             sheet_name=sub_asset_class_ranges_sheet_name,
                                                             file_name=file_name)
    else:
        sub_asset_class_ranges = None
    risk_factor_prices = load_risk_model_factor_prices(local_path=local_path, risk_model=risk_model)
    model_params = load_model_params(local_path=local_path)
    mac_universe_data = MacUniverseData(saa_prices=saa_prices,
                                        saa_universe_df=saa_universe_df,
                                        taa_prices=taa_prices,
                                        taa_universe_df=taa_universe_df,
                                        benchmarks=benchmarks,
                                        asset_class_ranges=asset_class_ranges,
                                        sub_asset_class_ranges=sub_asset_class_ranges,
                                        asset_loadings=asset_loadings,
                                        risk_factor_prices=risk_factor_prices,
                                        model_params=model_params)
    return mac_universe_data


# new fetchers
def fetch_portfolio_data(local_path: str,
                         universe_returns: pd.DataFrame,
                         portfolio: Union[SaaPortfolio, TaaPortfolio, str] = TaaPortfolio.TAA_FUNDS_MAC,
                         file_name: str = FEEDER_EXCEL_FILE
                         ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    fetch portfolio data from sheet
    """
    # special case
    if portfolio == SaaPortfolio.SAA_INDEX_PAPER:
        navs, universe_df = fetch_saa_index_paper_universe(local_path=local_path,
                                                           universe_returns=universe_returns,
                                                           file_name=file_name)
    else:

        if isinstance(portfolio, SaaPortfolio) or isinstance(portfolio, TaaPortfolio):  # enumerators
            sheet_name = portfolio.value
        else:
            sheet_name = portfolio
        universe_df = qis.load_df_from_excel(sheet_name=sheet_name,
                                             local_path=local_path,
                                             file_name=file_name)
        # remove nans
        is_nan_index = pd.Series(universe_df.index).isna().to_numpy(bool)
        universe_df = universe_df.iloc[is_nan_index == False, :]
        universe_df = universe_df.loc[:, ~universe_df.columns.duplicated(keep='last')]
        # temp solution
        if 'Cash' in universe_df.index:
            universe_df = universe_df.drop('Cash', axis=0)
        instrument_name_ticker_map = {ticker: name for name, ticker in
                                      universe_df[UniverseColumns.TICKER.value].to_dict().items()}
        tickers = list(instrument_name_ticker_map.keys())
        qis.assert_list_subset(large_list=universe_returns.columns, list_sample=tickers)
        returns = universe_returns[tickers].rename(instrument_name_ticker_map, axis=1)
        navs = qis.returns_to_nav(returns=returns).ffill()

    # create group loading
    # rudimentary way to check if asset class definition are included in taa universe
    if SUB_ASSET_CLASS_DEFINITIONS[0] in universe_df.columns:
        asset_loadings = universe_df[SUB_ASSET_CLASS_DEFINITIONS]
    else:
        asset_loadings = qis.set_group_loadings(group_data=universe_df[UniverseColumns.SUB_ASSET_CLASS.value])

    if UniverseColumns.CURRENT_WEIGHT.value not in universe_df.columns:
        universe_df[UniverseColumns.CURRENT_WEIGHT.value] = 0.0

    return navs, universe_df, asset_loadings


def fetch_saa_index_paper_universe(local_path: str,
                                   universe_returns: pd.DataFrame,
                                   file_name: str = FEEDER_EXCEL_FILE
                                   ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    universe_df = qis.load_df_from_excel(file_name=file_name, sheet_name='saa_index_paper', local_path=local_path)

    # generate universe prices
    returns = {}
    for instrument_name, row in universe_df.to_dict(orient='index').items():  # row is dict of columns values
        ticker1 = row['Ticker1']
        ticker2 = row['Ticker2']
        if instrument_name == 'Other Fixed Income':  # specific implementation for Other Fixed Income
            tickers = ['I13913US', 'LD19TRUU', 'H24641US', 'I38941US', 'BGCLTRUH']
            returns[instrument_name] = 0.2 * universe_returns[tickers].sum(1)
        elif (not isinstance(ticker2, str)) or ticker2 == '\xa0':  # np.isnan(ticker2):
            returns[instrument_name] = universe_returns[ticker1]
        else:
            return1 = universe_returns[ticker1]
            return2 = universe_returns[ticker2]
            weight1 = row['Weight1']
            weight2 = row['Weight2']
            returns[instrument_name] = weight1 * return1 + weight2 * return2

    returns = pd.DataFrame.from_dict(returns, orient='columns')
    navs = qis.returns_to_nav(returns=returns).ffill()
    return navs, universe_df


def fetch_risk_factors_from_saa_index_paper(local_path: str,
                                            universe_returns: Optional[pd.DataFrame] = None,
                                            risk_factors: List[str] = RISK_FACTORS
                                            ) -> pd.DataFrame:
    if universe_returns is None:
        universe_returns = load_universe_returns_from_sheet_data(local_path=local_path)
    navs, universe_df = fetch_saa_index_paper_universe(local_path=local_path, universe_returns=universe_returns)
    return navs[risk_factors]


def parse_sheet_descriptive_price_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # descriptive data
    with pd.option_context('future.no_silent_downcasting', True):
        df = df.replace({'\xa0': np.nan}).dropna(how='all', axis=1).dropna(how='all', axis=0)  # drop ll empty columns

    is_dates = {}
    for d in df.index:
        if not pd.isna(d):
            try:
                this = pd.to_datetime(d, dayfirst=True)
                is_dates[d] = True
            except:
                is_dates[d] = False
        else:
            is_dates[d] = False
    is_dates = pd.Series(is_dates)
    df = df.loc[~df.index.duplicated(keep='first')].reindex(index=is_dates.index)
    descriptive_data = df.loc[is_dates == False, :].copy()
    tickers = descriptive_data.loc['Main Ticker', :].to_list()
    # add instrument names
    descriptive_data.loc['Instrument Name', :] = descriptive_data.columns
    descriptive_data.columns = tickers
    descriptive_data.name = ''

    # returns
    returns_data = df.iloc[is_dates.to_numpy(bool), :].astype(float)
    returns_data.index = pd.to_datetime(returns_data.index, dayfirst=True)
    returns_data.columns = tickers
    returns_data.name = 'Date'

    return descriptive_data, returns_data


def load_universe_returns_from_sheet_data(local_path: str,
                                          verbose: bool = False,
                                          file_name: str = FEEDER_EXCEL_FILE
                                          ) -> pd.DataFrame:

    if not hasattr(load_universe_returns_from_sheet_data, '_universe_returns'):  # check sash

        index_df = qis.load_df_from_excel(file_name=file_name, sheet_name='Index Performance', local_path=local_path)
        index_descriptive_data, index_returns_data = parse_sheet_descriptive_price_data(df=index_df)
        if verbose:
            print(index_descriptive_data)
            print(index_returns_data)

        instrument_df = qis.load_df_from_excel(file_name=file_name, sheet_name='Instrument Performance',
                                               local_path=local_path)
        instrument_descriptive_data, instrument_returns_data = parse_sheet_descriptive_price_data(df=instrument_df)
        if verbose:
            print(instrument_descriptive_data)
            print(instrument_returns_data)

        universe_returns = pd.concat([index_returns_data, instrument_returns_data], axis=1)
        if verbose:
            print(universe_returns)

        universe_returns = universe_returns.loc[:, ~universe_returns.columns.duplicated(keep='first')]  # pe

        load_universe_returns_from_sheet_data._universe_returns = universe_returns

    return load_universe_returns_from_sheet_data._universe_returns.copy()


def load_asset_class_ranges(local_path: str,
                            sheet_name: str = 'saa_asset_class',
                            file_name: str = FEEDER_EXCEL_FILE
                            ) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name=file_name, sheet_name=sheet_name, local_path=local_path)
    return df


def load_sub_asset_class_ranges(local_path: str,
                                sheet_name: str = 'sub_asset_class_constraints',
                                file_name: str = FEEDER_EXCEL_FILE
                                ) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name=file_name, sheet_name=sheet_name, local_path=local_path)
    return df


def load_model_params(local_path: str) -> pd.DataFrame:
    df = qis.load_df_from_excel(file_name=FEEDER_EXCEL_FILE, sheet_name='model_params', local_path=local_path)
    return df


def load_risk_model_factor_prices(local_path: str,
                                  risk_model: RiskModel = RiskModel.PRICE_FACTORS_FROM_MAC_PAPER
                                  ) -> pd.DataFrame:
    if risk_model == RiskModel.PRICE_FACTORS_FROM_MAC_PAPER:
        risk_factor_prices = fetch_risk_factors_from_saa_index_paper(local_path=local_path)
    elif risk_model == RiskModel.FUTURES_RISK_FACTORS:
        risk_factor_prices = qis.load_df_from_csv(file_name='futures_risk_factors', local_path=lp.get_resource_path())
        risk_factor_prices = risk_factor_prices.resample('ME').last()
    else:
        raise NotImplementedError(f"risk_model={risk_model}")
    return risk_factor_prices


class LocalTests(Enum):
    SHEET_DATA = 1
    SAA_INDEX_UNIVERSE = 2
    TAA_INDEX_UNIVERSE = 3
    NEW_FETCHER = 4
    LOAD_MAC_UNIVERSE = 5
    LOAD_MAC_FUNDS_UNIVERSE = 7
    UPDATE_INDEX_DATA = 8
    APPEND_RETURNS_DATA = 9


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

    if local_test == LocalTests.SHEET_DATA:
        universe_returns = load_universe_returns_from_sheet_data(local_path=local_path, verbose=True)
        risk_factor_prices = fetch_risk_factors_from_saa_index_paper(local_path=local_path,
                                                                     universe_returns=universe_returns)
        qis.save_df_to_csv(risk_factor_prices, file_name='risk_factor_prices', local_path=local_path)

    elif local_test == LocalTests.SAA_INDEX_UNIVERSE:
        universe_returns = load_universe_returns_from_sheet_data(local_path=local_path)
        saa_prices, saa_universe_df = fetch_saa_index_paper_universe(local_path=local_path,
                                                                     universe_returns=universe_returns)
        #qis.save_df_to_excel(data=dict(navs=navs, universe_df=universe_df), file_name='saa_index_universe', local_path=local_path)
        print(saa_prices)
        print(saa_universe_df)

    elif local_test == LocalTests.NEW_FETCHER:
        universe_returns = load_universe_returns_from_sheet_data(local_path=local_path, verbose=True)
        navs, universe_df, asset_loadings = fetch_portfolio_data(local_path=local_path,
                                                                 universe_returns=universe_returns,
                                                                 portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                                 file_name=FEEDER_EXCEL_FILE)
        print(navs)
        print(universe_df)
        print(asset_loadings)

    elif local_test == LocalTests.LOAD_MAC_UNIVERSE:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                    file_name=FEEDER_EXCEL_FILE)
        #print(universe_data)

        this = universe_data.get_saa_constraints()
        print(this)

        this = universe_data.get_taa_constraints()
        print(this)

        this = universe_data.get_taa_asset_class_data(is_merge_alts_with_equity=True)
        print(this)

        this = universe_data.get_joint_turnover_groups()
        print(this)

        this = universe_data.get_joint_turnover_order()
        print(this)

        prices = universe_data.get_joint_prices()
        prices_unsmoothed = universe_data.get_joint_prices(apply_unsmoothing_for_pe=True)
        qis.save_df_to_excel(data=dict(prices=prices, prices_unsmoothed=prices_unsmoothed), file_name='mac_prices',
                             local_path=local_path)

    elif local_test == LocalTests.LOAD_MAC_FUNDS_UNIVERSE:
        # sub_asset_class_constraints
        mac_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                        saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                        taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC,
                                                        sub_asset_class_ranges_sheet_name='sub_asset_class_constraints1')
        print(mac_universe_data)
        this = mac_universe_data.get_taa_constraints()
        print(this)

    elif local_test == LocalTests.UPDATE_INDEX_DATA:
        from bbg_fetch import fetch_field_timeseries_per_tickers
        index_df = qis.load_df_from_excel(file_name=FEEDER_EXCEL_FILE, sheet_name='Index Performance',
                                          local_path=local_path)
        index_descriptive_data, index_returns_data = parse_sheet_descriptive_price_data(df=index_df)

        tickers = {f"{x} Index": x for x in index_returns_data.columns}
        #tickers.remove('MSCI PE Index')
        #tickers.remove('MSCI PD Index')
        prices = fetch_field_timeseries_per_tickers(tickers=tickers, start_date=pd.Timestamp('31Dec2023')).ffill()
        print(prices)

        dates = pd.DatetimeIndex(['30Nov2024', '31Dec2024', '31Jan2025', '28Feb2025'])
        print(dates)
        returns = prices.reindex(index=dates, method='ffill').pct_change()
        print(returns)
        returns.to_clipboard()

    elif local_test == LocalTests.APPEND_RETURNS_DATA:
        index_df = qis.load_df_from_excel(file_name=FEEDER_EXCEL_FILE, sheet_name='Index Performance',
                                          local_path=local_path)


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.LOAD_MAC_UNIVERSE)
