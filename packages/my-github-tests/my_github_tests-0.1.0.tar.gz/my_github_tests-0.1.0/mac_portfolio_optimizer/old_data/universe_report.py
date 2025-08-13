import pandas as pd
import qis as qis
import matplotlib.pyplot as plt
from enum import Enum
from qis import PerfStat
from mac_portfolio_optimizer.data.mac_universe import MacUniverseData
from mac_portfolio_optimizer.data.excel_loader import load_mac_portfolio_universe, SaaPortfolio, TaaPortfolio


BENCHMARK_TABLE_COLUMNS = (PerfStat.START_DATE,
                           PerfStat.PA_RETURN,
                           PerfStat.VOL,
                           PerfStat.SHARPE_EXCESS,
                           PerfStat.MAX_DD,
                           PerfStat.SKEWNESS,
                           PerfStat.ALPHA_AN,
                           PerfStat.BETA,
                           PerfStat.R2)


def plot_frontier(universe_data: MacUniverseData,
                  last_time_period: qis.TimePeriod = qis.TimePeriod('31Dec2019', None)
                  ):

    prices = universe_data.taa_prices
    prices = pd.concat([universe_data.benchmarks, prices], axis=1)

    kwargs = dict(perf_params=qis.PerfParams(freq='ME'), alpha_an_factor=12.0, perf_columns=BENCHMARK_TABLE_COLUMNS)

    qis.plot_ra_perf_table_benchmark(prices, benchmark=universe_data.benchmarks.columns[0],
                                     title=qis.get_time_period(prices).to_str(),
                                     **kwargs)

    prices = last_time_period.locate(prices)
    qis.plot_ra_perf_table_benchmark(prices, benchmark=universe_data.benchmarks.columns[0],
                                     title=qis.get_time_period(prices).to_str(),
                                     **kwargs)

    qis.plot_ra_perf_scatter(prices=prices,
                             x_var=PerfStat.VOL,
                             y_var=PerfStat.PA_RETURN,
                             order=2)


class LocalTests(Enum):
    FUNDS_UNIVERSE = 1


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

    if local_test == LocalTests.FUNDS_UNIVERSE:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)
        plot_frontier(universe_data)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.FUNDS_UNIVERSE)
