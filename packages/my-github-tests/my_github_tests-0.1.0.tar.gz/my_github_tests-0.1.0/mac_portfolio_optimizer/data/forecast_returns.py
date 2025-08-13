"""
returns extrapolation
"""
import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
from enum import Enum

from optimalportfolios.lasso.lasso_model_estimator import solve_lasso_cvx_problem

# universe data
from mac_portfolio_optimizer import (load_universe_returns_from_sheet_data,
                                     load_mac_portfolio_universe,
                                     SaaPortfolio,
                                     TaaPortfolio)


def extrapolate_return(risk_factors: pd.DataFrame,
                       given_price: pd.Series
                       ):
    risk_factors_1 = risk_factors.reindex(index=given_price.index, method='ffill')

    # estimate lasso
    y = qis.to_returns(given_price, drop_first=True)
    x_1 = qis.to_returns(risk_factors_1, drop_first=True)
    y_mean = np.nanmean(y, axis=0)
    params = dict(reg_lambda=1e-5, span=24, nonneg=False)
    beta3_, _ = solve_lasso_cvx_problem(x=x_1.to_numpy() - np.nanmean(x_1, axis=0),
                                    y=y.to_numpy() - y_mean,
                                    **params, apply_independent_nan_filter=False)

    # do forecast
    x_forecast = qis.to_returns(risk_factors, drop_first=True)
    risk_factors_forecast = x_forecast.loc[x_forecast.index > x_1.index[-1], :]

    forecast_return = y_mean + risk_factors_forecast @ beta3
    return forecast_return


class LocalTests(Enum):
    PE_EXTRAPOLATE = 1
    INSTRUMENT_EXTRAPOLATE = 2


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

    universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)

    universe_navs = qis.returns_to_nav(load_universe_returns_from_sheet_data(local_path=local_path))

    if local_test == LocalTests.PE_EXTRAPOLATE:
        risk_factors = universe_data.get_risk_factors().asfreq('QE')
        assets = ['MSCI PE', 'MSCI PD']
        for asset in assets:
            given_price = universe_navs[asset].asfreq('QE').iloc[:-1]
            forecast_return = extrapolate_return(risk_factors=risk_factors,
                                                 given_price=given_price)
            print(forecast_return.rename(asset))

    elif local_test == LocalTests.INSTRUMENT_EXTRAPOLATE:
        risk_factors = universe_data.get_risk_factors().asfreq('ME')
        assets = ['STECHOF KY',
                  'LGTSTHU ID',
                  'HLGPAFI LX',
                  'HALSCIU LX',
                  'LGTMTAJ LE',
                  'LGPSUSB LE']  # -1
        assets = ['LU2947921800',
                  'ASIFDUA LX']  # -1
        for asset in assets:
            given_price = universe_navs[asset].asfreq('ME').iloc[:-1]
            forecast_return = extrapolate_return(risk_factors=risk_factors,
                                                 given_price=given_price)
            print(forecast_return.rename(asset))

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.INSTRUMENT_EXTRAPOLATE)
