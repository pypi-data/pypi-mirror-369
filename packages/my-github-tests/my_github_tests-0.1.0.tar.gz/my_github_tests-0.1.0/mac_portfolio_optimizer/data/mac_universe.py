"""
definition of mac universe which is represented as data class object
"""
import numpy as np
import pandas as pd
import qis as qis
from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict, Optional
from enum import Enum
from optimalportfolios import (GroupLowerUpperConstraints,
                               Constraints,
                               GroupTurnoverConstraint,
                               merge_group_lower_upper_constraints,
                               GroupTrackingErrorConstraint,
                               compute_ar1_unsmoothed_prices)


SUB_ASSET_CLASS_DEFINITIONS_PAPER = ['Rates', 'Credit', 'HY Credit', 'EM Bonds', 'Other Fixed Income',
                                     'Equity',
                                     'Hedge Funds', 'Private Equity', 'Private Debt', 'Real Assets', 'Insurance-Linked']

SUB_ASSET_CLASS_DEFINITIONS = ['Rates', 'Credit', 'EM Bonds', 'Other Fixed Income',
                               'Equity',
                               'Hedge Funds', 'Private Equity', 'Private Debt', 'Real Assets', 'Insurance-Linked']

RISK_FACTORS = ['Rates', 'Credit', 'HY Credit', 'EM Bonds', 'Equity', 'Hedge Funds', 'Real Assets']

PE_ASSET_FOR_UNSMOOTHING = ['Private Equity', 'Private Debt', 'Insurance-Linked', 'Private Assets',
                            'LGT Multi-Strategy (LMA)', 'Fermat CAT Bond Fund-F USD',
                            'Hamilton Lane Global Private Assets Fund',
                            'Franklin Lexington Private Markets Fund SICAV - Flex Feeder I USD',
                            'PG3 Longreach Alternative Strategies Fund ',
                            'Ares Strategic Income Offshore Access Fund USD',
                            'Hamilton Lane Senior Credit Opportunities Fund I - USD'
                            ]


class RiskModel(Enum):
    PRICE_FACTORS_FROM_MAC_PAPER = 1
    FUTURES_RISK_FACTORS = 2


class AssetClasses(str, Enum):  # supported asset classes
    FI = 'Fixed Income'
    EQ = 'Equity'
    ALTS = 'Alternatives'
    LIQUIDITY = 'Liquidity'


class SaaPortfolio(str, Enum):  # implemented saa portfolios
    # implemented in 'MAC Allocation Tracker v.4'
    SAA_INDEX_MAC = 'saa_index_mac'
    SAA_INDEX_PAPER = 'saa_index_paper'
    SAA_BALANCED_APAC = 'saa_index_RgBalAPAC'
    # implemented in 'Step 1 SAA - Artur'
    APAC_INCOME = 'saa_index_RgIncAPAC'
    APAC_CONSERVATIVE = 'saa_index_RgConAPAC'
    APAC_BALANCED = 'saa_index_RgBalAPAC'
    APAC_GROWTH = 'saa_index_RgGroAPAC'
    APAC_EQUITIES = 'saa_index_RgEqtAPAC'


class TaaPortfolio(str, Enum):  # implemented taa portfolios
    # implemented in 'MAC Allocation Tracker v.4'
    TAA_FUNDS_MAC = 'taa_fund_mac'
    TAA_INDEX_PAPER = 'taa_index_paper'


class MacRangeConstraints(Enum):  # implemented mac range constraints
    UNCONSTRAINT = None
    TYPE1 = 'sub_asset_class_constraints1'
    TYPE2 = 'sub_asset_class_constraints2'


class SaaRangeConstraints(str, Enum):  # implemented saa range constraints
    # implemented in 'MAC Allocation Tracker v.4'
    MAC_SAA_RANGES = 'saa_asset_class'
    # implemented in 'Step 1 SAA - Artur'
    APAC_INCOME = 'saa_asset_class_RgIncAPAC'
    APAC_CONSERVATIVE = 'saa_asset_class_RgConAPAC'
    APAC_BALANCED = 'saa_asset_class_RgBalAPAC'
    APAC_GROWTH = 'saa_asset_class_RgGroAPAC'
    APAC_EQUITIES = 'saa_asset_class_RgEqtAPAC'


class UniverseColumns(Enum):
    # mandatory universe data for saa_universe_df and taa_universe_df dfs
    TICKER = 'Ticker'
    ASSET_CLASS = 'Asset Class'
    SUB_ASSET_CLASS = 'Sub Asset Class'
    MAX = 'Max'
    MIN = 'Min'
    ALPHA_BETA = 'Alpha/Beta'
    TURNOVER_GROUP = 'Turnover Group'
    REBALANCING = 'Rebalancing'

    # optional for taa fund rebalncing
    CURRENT_WEIGHT = 'Current Weight'
    CURRENT_MIN = 'Current Min'
    CURRENT_MAX = 'Current Max'

    # optional for SAA
    BENCHMARK_STATIC_WEIGHT = 'Benchmark Static Weight'
    RISK_BUDGET = 'Risk Budget'


@dataclass
class MacUniverseData:
    saa_prices: pd.DataFrame
    saa_universe_df: pd.DataFrame
    taa_prices: pd.DataFrame
    taa_universe_df: pd.DataFrame
    asset_class_ranges: pd.DataFrame
    risk_factor_prices: pd.DataFrame  # risk factors
    benchmarks: pd.DataFrame = None  # cash benchmark
    asset_loadings: Optional[pd.DataFrame] = None  # bespoke asset loaings
    sub_asset_class_ranges: Optional[pd.DataFrame] = None
    model_params: Optional[pd.DataFrame] = None
    cmas: Optional[pd.DataFrame] = None

    # group related
    ac_group_order: List[str] = tuple([x.value for x in AssetClasses])
    sub_ac_group_order: List[str] = tuple(SUB_ASSET_CLASS_DEFINITIONS)
    return_annualisation_freq_dict = {'ME': 12.0, 'QE': 4.0, 'YE': 1.0}  # for annualisation of excess returns

    def to_dict(self):
        return asdict(self)

    def get_saa_asset_class_data(self) -> pd.Series:
        return self.saa_universe_df[UniverseColumns.ASSET_CLASS.value]

    def get_saa_sub_asset_class_data(self) -> pd.Series:
        return self.saa_universe_df[UniverseColumns.SUB_ASSET_CLASS.value]

    def get_taa_asset_class_data(self, is_merge_alts_with_equity: bool = False) -> pd.Series:
        """
        is_merge_alts_with_equity = True for groups alpha computation
        """
        asset_class_data = self.taa_universe_df[UniverseColumns.ASSET_CLASS.value]
        if is_merge_alts_with_equity:
            asset_class_data = asset_class_data.replace({AssetClasses.ALTS.value: AssetClasses.EQ.value})
        return asset_class_data

    def get_taa_sub_asset_class_data(self) -> pd.Series:
        return self.taa_universe_df[UniverseColumns.SUB_ASSET_CLASS.value]

    def get_saa_rename_dict(self) -> Dict[str, str]:
        """
        to distinguish between taa and saa assets
        """
        return {x: f"{x} *" for x in self.saa_prices.columns}

    def get_taa_rename_dict(self) -> Dict[str, str]:
        """
        make anonymous names
        """
        return {x: f"Asset-{idx+1}" for idx, x in enumerate(self.taa_prices.columns)}

    def get_saa_prices(self,
                       add_star_to_saa_names: bool = False,
                       time_period: qis.TimePeriod = None,
                       apply_unsmoothing_for_pe: bool = False,
                       unsmooth_span: int = 20
                       ) -> pd.DataFrame:
        prices = self.saa_prices.copy()
        if apply_unsmoothing_for_pe:
            pe_assets = qis.list_intersection(list_check=PE_ASSET_FOR_UNSMOOTHING, list_sample=prices.columns)
            pe_prices, _, _, _ = compute_ar1_unsmoothed_prices(prices=prices[pe_assets],
                                                                    freq='QE',
                                                                    span=unsmooth_span)
            prices[pe_assets] = pe_prices.reindex(index=prices.index).ffill()
            prices = prices[self.saa_prices.columns]
        if add_star_to_saa_names:
            prices = prices.rename(self.get_saa_rename_dict(), axis=1)
        if time_period is not None:
            prices = time_period.locate(prices)
        return prices

    def get_taa_prices(self,
                       anonymise_taa_names: bool = False,
                       time_period: qis.TimePeriod = None,
                       apply_unsmoothing_for_pe: bool = False,
                       unsmooth_span: int = 20
                       ) -> pd.DataFrame:
        prices = self.taa_prices.copy()
        if apply_unsmoothing_for_pe:
            pe_assets = qis.list_intersection(list_check=PE_ASSET_FOR_UNSMOOTHING, list_sample=prices.columns)
            pe_prices, _, _, _ = compute_ar1_unsmoothed_prices(prices=prices[pe_assets],
                                                               freq='QE',
                                                               span=unsmooth_span)
            prices[pe_assets] = pe_prices.reindex(index=prices.index).ffill()
            prices = prices[self.taa_prices.columns]
        if anonymise_taa_names:
            prices = prices.rename(self.get_taa_rename_dict(), axis=1)
        if time_period is not None:
            prices = time_period.locate(prices)
        return prices

    def get_joint_prices(self,
                         add_star_to_saa_names: bool = False,
                         anonymise_taa_names: bool = False,
                         time_period: qis.TimePeriod = None,
                         apply_unsmoothing_for_pe: bool = False,
                         unsmooth_span: int = 20
                         ) -> pd.DataFrame:
        joint_assets = qis.merge_lists_unique(self.saa_prices.columns, self.taa_prices.columns)
        joint_prices = pd.concat([self.saa_prices, self.taa_prices], axis=1)
        joint_prices = joint_prices.loc[:, ~joint_prices.columns.duplicated(keep='first')]

        if apply_unsmoothing_for_pe:
            pe_assets = qis.list_intersection(list_check=PE_ASSET_FOR_UNSMOOTHING, list_sample=joint_prices.columns)
            pe_prices, _, _, _  = compute_ar1_unsmoothed_prices(prices=joint_prices[pe_assets],
                                                                freq='QE',
                                                                span=unsmooth_span)
            joint_prices[pe_assets] = pe_prices.reindex(index=joint_prices.index).ffill()
        joint_prices = joint_prices[joint_assets]  # arrange

        if add_star_to_saa_names:
            joint_prices = joint_prices.rename(self.get_saa_rename_dict(), axis=1)
        if anonymise_taa_names:
            joint_prices = joint_prices.rename(self.get_taa_rename_dict(), axis=1)
        if time_period is not None:
            joint_prices = time_period.locate(joint_prices)
        return joint_prices

    def get_joint_assets(self,
                         add_star_to_saa_names: bool = False,
                         anonymise_taa_names: bool = False
                         ) -> List[str]:
        joint_prices = self.get_joint_prices(add_star_to_saa_names=add_star_to_saa_names,
                                             anonymise_taa_names=anonymise_taa_names)
        return joint_prices.columns.to_list()

    def get_joint_ac_group_data(self) -> Tuple[pd.Series, List[str]]:
        saa_group_data = self.get_saa_asset_class_data()
        taa_group_data = self.get_taa_asset_class_data()
        joint_ac = pd.concat([saa_group_data, taa_group_data])
        joint_ac = joint_ac[~joint_ac.index.duplicated()][self.get_joint_assets()]
        return joint_ac, self.ac_group_order

    def get_joint_sub_ac_group_data(self) -> Tuple[pd.Series, List[str]]:
        saa_group_data = self.get_saa_sub_asset_class_data()
        taa_group_data = self.get_taa_sub_asset_class_data()
        joint_ac = pd.concat([saa_group_data, taa_group_data])
        joint_ac = joint_ac[~joint_ac.index.duplicated()][self.get_joint_assets()]
        return joint_ac, self.sub_ac_group_order

    def get_benchmark_static_weights(self) -> pd.Series:
        return self.saa_universe_df[UniverseColumns.BENCHMARK_STATIC_WEIGHT.value]

    def get_saa_risk_budget(self) -> pd.Series:
        return self.saa_universe_df[UniverseColumns.RISK_BUDGET.value]

    def get_saa_turnover_groups(self) -> pd.Series:
        return self.saa_universe_df[UniverseColumns.TURNOVER_GROUP.value]

    def get_taa_turnover_groups(self) -> pd.Series:
        return self.taa_universe_df[UniverseColumns.TURNOVER_GROUP.value]

    def get_joint_turnover_groups(self) -> pd.Series:
        taa_turnover_groups = self.get_taa_turnover_groups()
        # fill saa group with 0: it will be ignored anyway
        joint_turnover_groups = taa_turnover_groups.reindex(index=self.get_joint_assets()).fillna(0)
        return joint_turnover_groups

    def get_joint_turnover_order(self) -> List[str]:
        joint_turnover_groups = self.get_joint_turnover_groups()
        turnover_order = joint_turnover_groups.unique().tolist()
        turnover_order.sort()
        return turnover_order

    def get_saa_rebalancing_freqs(self) -> pd.Series:
        return self.saa_universe_df[UniverseColumns.REBALANCING.value].astype(str)

    def get_taa_rebalancing_freqs(self) -> pd.Series:
        return self.taa_universe_df[UniverseColumns.REBALANCING.value].astype(str)

    def get_joint_rebalancing_freqs(self,
                                    add_star_to_saa_names: bool = False,
                                    anonymise_taa_names: bool = False
                                    ) -> pd.Series:
        saa_rebalancing_freqs = self.get_saa_rebalancing_freqs()
        taa_rebalancing_freqs = self.get_taa_rebalancing_freqs()
        if add_star_to_saa_names:
            saa_rebalancing_freqs = saa_rebalancing_freqs.rename(self.get_saa_rename_dict(), axis=0)
        if anonymise_taa_names:
            taa_rebalancing_freqs = taa_rebalancing_freqs.rename(self.get_taa_rename_dict(), axis=0)

        rebalancing_freqs = pd.concat([saa_rebalancing_freqs, taa_rebalancing_freqs])
        # align to joint_assets
        joint_assets = self.get_joint_assets(add_star_to_saa_names=add_star_to_saa_names,
                                             anonymise_taa_names=anonymise_taa_names)
        rebalancing_freqs = rebalancing_freqs[~rebalancing_freqs.index.duplicated()][joint_assets]
        return rebalancing_freqs

    def get_saa_constraints(self, add_max_ac_constraints: bool = True) -> Constraints:
        ac_df = self.asset_class_ranges
        saa_loadings = qis.set_group_loadings(group_data=self.get_saa_asset_class_data())
        if add_max_ac_constraints:
            saa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=saa_loadings,
                                                                           group_min_allocation=None,
                                                                           group_max_allocation=ac_df[UniverseColumns.MAX.value])
        else:
            saa_group_lower_upper_constraints = GroupLowerUpperConstraints(group_loadings=saa_loadings,
                                                                           group_min_allocation=ac_df[UniverseColumns.MIN.value],
                                                                           group_max_allocation=ac_df[UniverseColumns.MAX.value])

        saa_constraints = Constraints(min_weights=self.saa_universe_df[UniverseColumns.MIN.value],
                                      max_weights=self.saa_universe_df[UniverseColumns.MAX.value],
                                      group_lower_upper_constraints=saa_group_lower_upper_constraints,
                                      apply_total_to_good_ratio_for_constraints=False)

        return saa_constraints

    def get_taa_constraints(self,
                            use_current_min_max: bool = False,
                            global_tracking_err_vol_constraint: Optional[float] = None,
                            group_tracking_err_vol_constraint: Optional[pd.Series] = None,
                            global_max_turnover_constraint: Optional[float] = None,
                            group_max_turnover_constraint: Optional[pd.Series] = None
                            ) -> Constraints:
        ac_df = self.asset_class_ranges
        joint_ac, _ = self.get_joint_ac_group_data()
        joint_assets = self.get_joint_assets()

        taa_group_lower_upper_constraints = GroupLowerUpperConstraints(
            group_loadings=qis.set_group_loadings(group_data=joint_ac),
            group_min_allocation=ac_df[UniverseColumns.MIN.value],
            group_max_allocation=ac_df[UniverseColumns.MAX.value])

        if self.sub_asset_class_ranges is not None:
            if self.asset_loadings is not None:
                group_loadings = self.asset_loadings
            else:
                joint_sub_ac, _ = self.get_joint_sub_ac_group_data()
                group_loadings = qis.set_group_loadings(group_data=joint_sub_ac)

            # limit subacs loading
            constraints_sub_acs = self.sub_asset_class_ranges.index.to_list()
            group_loadings = group_loadings[constraints_sub_acs]
            taa_subgroup_lower_upper_constraints = GroupLowerUpperConstraints(
                group_loadings=group_loadings,
                group_min_allocation=self.sub_asset_class_ranges[UniverseColumns.MIN.value],
                group_max_allocation=self.sub_asset_class_ranges[UniverseColumns.MAX.value])



        with pd.option_context('future.no_silent_downcasting', True):
            if use_current_min_max:
                taa_min_weights = self.taa_universe_df[UniverseColumns.CURRENT_MIN.value].reindex(index=joint_assets).fillna(0.0)
                taa_max_weights = self.taa_universe_df[UniverseColumns.CURRENT_MAX.value].reindex(index=joint_assets).fillna(0.0)
            else:
                taa_min_weights = self.taa_universe_df[UniverseColumns.MIN.value].reindex(index=joint_assets).fillna(0.0)
                taa_max_weights = self.taa_universe_df[UniverseColumns.MAX.value].reindex(index=joint_assets).fillna(0.0)

        # tracking error
        if group_tracking_err_vol_constraint is not None:
            joint_ac, _ = self.get_joint_ac_group_data()
            taa_group_tracking_error_constraint = GroupTrackingErrorConstraint(group_loadings=qis.set_group_loadings(group_data=joint_ac),
                                                                               group_tre_vols=group_tracking_err_vol_constraint)
            global_tracking_err_vol_constraint = None  # ignore
        else:
            taa_group_tracking_error_constraint = None

        # turnover
        if group_max_turnover_constraint is not None:
            joint_turnover_group = self.get_joint_turnover_groups()
            turnover_groups = qis.set_group_loadings(group_data=joint_turnover_group)
            group_turnover_constraint = GroupTurnoverConstraint(group_loadings=turnover_groups,
                                                                group_max_turnover=group_max_turnover_constraint)
        else:
            group_turnover_constraint = None
        taa_constraints = Constraints(min_weights=taa_min_weights,
                                      max_weights=taa_max_weights,
                                      group_lower_upper_constraints=taa_group_lower_upper_constraints,
                                      apply_total_to_good_ratio_for_constraints=False,
                                      # turnover_costs=self.get_turnover_groups(),
                                      group_tracking_error_constraint=taa_group_tracking_error_constraint,
                                      tracking_err_vol_constraint=global_tracking_err_vol_constraint,
                                      group_turnover_constraint=group_turnover_constraint,
                                      turnover_constraint=global_max_turnover_constraint)

        return taa_constraints

    def set_group_uniform_tracking_error_constraint(self, tracking_err_vol_constraint: float) -> pd.Series:
        group_tracking_error_constraint = pd.Series(tracking_err_vol_constraint, index=tuple([x.value for x in AssetClasses]))
        return group_tracking_error_constraint

    def get_taa_current_weights(self) -> Optional[pd.Series]:
        if UniverseColumns.CURRENT_WEIGHT.value in self.taa_universe_df.columns:
            with pd.option_context('future.no_silent_downcasting', True):
                taa_current_weights = self.taa_universe_df[UniverseColumns.CURRENT_WEIGHT.value].replace({'\xa0': np.nan}).astype(float).fillna(0.0)
        else:
            taa_current_weights = None
        return taa_current_weights

    def get_alpha_beta_type(self) -> pd.Series:
        return self.taa_universe_df[UniverseColumns.ALPHA_BETA.value]

    def get_risk_factors(self, time_period: qis.TimePeriod = None) -> pd.DataFrame:
        prices = self.risk_factor_prices.copy()
        if time_period is not None:
            prices = time_period.locate(prices)
        return prices

    def compute_static_weight_saa_benchmark(self,
                                            weights: pd.Series = None,
                                            management_fee: float = 0.0,
                                            rebalancing_freq: str = 'QE',
                                            ticker: str = 'Static BM'
                                            ) -> pd.Series:
        if weights is None:
            weights = self.saa_universe_df[UniverseColumns.BENCHMARK_STATIC_WEIGHT.value]
        eq_benchmark = qis.backtest_model_portfolio(prices=self.saa_prices,
                                                    weights=weights,
                                                    rebalancing_freq=rebalancing_freq,
                                                    management_fee=management_fee,
                                                    ticker=ticker).get_portfolio_nav(freq='ME')
        return eq_benchmark
