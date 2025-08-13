import pandas as pd
import numpy as np
import qis as qis
from typing import Tuple, Optional, Union, List
from enum import Enum

from mac_portfolio_optimizer import SaaPortfolio, load_mac_portfolio_universe
from mac_portfolio_optimizer.local_path import LOCAL_PATH

FEEDER_EXCEL_FILE1 = 'Step 1 SAA - Artur'


def load_range_mandate(local_path: str, excel_feeder_file: str = FEEDER_EXCEL_FILE1):
    mac_universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.APAC_INCOME,
                                                    taa_portfolio=None,
                                                    file_name=excel_feeder_file)
    print(mac_universe_data)
    this = mac_universe_data.get_taa_constraints()
    print(this)


class LocalTests(Enum):
    LOAD_RANGE_MANDATE = 1


@qis.timer
def run_local_test(local_test: LocalTests):
    """Run local tests for development and debugging purposes.

    These are integration tests that download real data and generate reports.
    Use for quick verification during development.
    """
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    local_path = LOCAL_PATH

    if local_test == LocalTests.LOAD_RANGE_MANDATE:
        load_range_mandate(local_path=local_path)



if __name__ == '__main__':

    run_local_test(local_test=LocalTests.LOAD_RANGE_MANDATE)
