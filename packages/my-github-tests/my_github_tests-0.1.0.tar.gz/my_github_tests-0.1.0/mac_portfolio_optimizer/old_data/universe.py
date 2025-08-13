"""
definition of instrument data class
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List
from optimalportfolios import Constraints
from qis import backtest_model_portfolio

# class SpreadSheetColumns(Enum):
BENCHMARK = 'Investable Benchmark'
BENCHMARK_WEIGHT = 'Benchmark Weight'
SAA_BENCHMARK_BUDGET = 'Benchmark SAA Risk Budget'
INCLUDED_FOR_SAA = 'SAA Inclusion'
INCLUDED_FOR_TAA = 'TAA Inclusion'
BENCHMARK_CONSTITUENTS = 'Benchmark Constituents'
SAA_MIN = 'SAA Min'
SAA_MAX = 'SAA Max'
TAA_MIN = 'TAA Min'
TAA_MAX = 'TAA Max'
REBALANCING = 'Rebalancing'
ASSET_CLASS = 'Asset Class'
BENCHMARK_STATIC_WEIGHT = 'StaticWeight'
GIM_NAME = 'LGT GIM B'
STATIC_BENCHMARK_NAME = 'Static BM'


@dataclass
class UniverseData:
    saa_prices: pd.DataFrame  # for saa allocation
    taa_prices: pd.DataFrame  # for taa allocation
    joint_prices: pd.DataFrame  # for both saa+taa allocation
    risk_factors_prices: pd.DataFrame  # for risk factors
    saa_benchmark_budgets_df: pd.DataFrame
    saa_assets_budgets: pd.Series  # extrapolated to asset universe
    saa_constraints: Constraints
    taa_constraints: Constraints
    rebalancing_freqs: pd.Series
    group_data_sub_ac: pd.Series
    group_order_sub_ac: List[str]
    group_data: pd.Series
    group_order: List[str]
    descriptive_df: pd.DataFrame
    benchmarks: pd.DataFrame  # cash benchmark

    def get_asset_names_dict(self) -> Dict[str, str]:
        if 'Asset' in self.descriptive_df.columns:
            return self.descriptive_df['Asset'].to_dict()
        else:
            return {x: x for x in self.descriptive_df.index}

    def compute_static_weight_saa_benchmark(self, management_fee: float = 0.0) -> pd.Series:
        eq_benchmark = backtest_model_portfolio(prices=self.saa_prices,
                                                weights=self.saa_benchmark_budgets_df[BENCHMARK_STATIC_WEIGHT],
                                                rebalancing_freq='QE',
                                                management_fee=management_fee,
                                                ticker=STATIC_BENCHMARK_NAME).get_portfolio_nav(freq='ME')
        return eq_benchmark
