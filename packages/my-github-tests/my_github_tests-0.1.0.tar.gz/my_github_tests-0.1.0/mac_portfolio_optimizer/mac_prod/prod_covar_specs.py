"""
specs of production covar estimator
"""
import pandas as pd
from typing import Union

from optimalportfolios import CovarEstimator, LassoModel, LassoModelType, CovarEstimatorType


def get_prod_covar_estimator(rebalancing_freq: str = 'ME',
                             apply_unsmoothing_for_pe: bool = False,
                             returns_freqs: Union[str, pd.Series] = 'ME'
                             ) -> CovarEstimator:
    lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                             group_data=None,
                             demean=True,
                             reg_lambda=1e-5,  # 2.5*1e-5
                             span=36,
                             solver='ECOS_BB',
                             warmup_period=12,
                             exclude_zero_betas=False
                             )

    # set covar estimator
    if apply_unsmoothing_for_pe:
        is_adjust_for_newey_west = False
        num_lags_newey_west = None
    else:
        is_adjust_for_newey_west = True
        num_lags_newey_west = {'ME': 0, 'QE': 2}
    covar_estimator = CovarEstimator(covar_estimator_type=CovarEstimatorType.LASSO,
                                     lasso_model=lasso_model,
                                     factor_returns_freq='ME',
                                     rebalancing_freq=rebalancing_freq,  # taa rebalancing
                                     returns_freqs=returns_freqs,
                                     span=lasso_model.span,
                                     is_apply_vol_normalised_returns=False,
                                     squeeze_factor=0.0,
                                     residual_var_weight=1.0,
                                     span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span / 4},
                                     var_scaler_freq_dict={'ME': 1.0, 'QE': 1.0/4.0, 'YE': 1.0/12.0},  # for scaling of vars and covars to monthly vols,
                                     is_adjust_for_newey_west=is_adjust_for_newey_west,
                                     num_lags_newey_west=num_lags_newey_west
                                     )
    return covar_estimator
