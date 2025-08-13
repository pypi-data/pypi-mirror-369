"""
define columns in the feeder spreadsheet
and maps from excel columns to MAC standard columns
"""
from mac_portfolio_optimizer.data.mac_universe import UniverseColumns
from enum import Enum


class SaaUniverseColumns(str, Enum):
    # excel columns
    TICKER = 'BBTickerFull'
    FAMILY = 'Family'
    BASE_CCY = 'BaseCcy'
    RISK_PROFILE = 'RiskProfile'
    ALT_INV = 'AltInv'
    AA_TYPE = 'AAType'
    AC_KEY = 'AC_key'
    WEIGHT = 'Weight'
    AC_LEVEL1 = 'ACLvl1'
    AC_LEVEL2 = 'ACLvl2'


SAA_TO_MAC_COLUMNS_MAP = {SaaUniverseColumns.AC_LEVEL1.value: UniverseColumns.ASSET_CLASS.value,
                          SaaUniverseColumns.AC_LEVEL2.value: UniverseColumns.SUB_ASSET_CLASS.value,
                          SaaUniverseColumns.WEIGHT.value: UniverseColumns.BENCHMARK_STATIC_WEIGHT.value}

SAA_AC_LEVEL1 = ['Equities', 'Bonds', 'Alternative', 'Money Market']

class Family(str, Enum):
    CLASSIC = 'Classic'


class BaseCcy(str, Enum):
    CHF = 'CHF'
    EUR = 'EUR'
    GBP = 'GBP'
    USD = 'USD'


class RiskProfile(str, Enum):
    VERY_LOW = 'Very Low'
    LOW = 'Low'
    MODERATE = 'Moderate'
    HIGH = 'High'
    VERY_HIGH = 'Very High'


class AltIntType(str, Enum):
    AI = 'AI'
    EX = 'EX'


class CmaType(str, Enum):
    LGT_CMAS = 'lgt_cmas'
    AQR = 'aqr_cmas'
    US_NO_VALUATION = 'lgt_cmas_no_valuation'
    HISTORICAL_10Y = 'historical_10y'
    FIXED_SHARPE = 'fixed_sharpe'