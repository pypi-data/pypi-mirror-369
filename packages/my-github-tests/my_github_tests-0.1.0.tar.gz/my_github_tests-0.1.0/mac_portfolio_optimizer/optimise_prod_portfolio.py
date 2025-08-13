"""
script for running the prod optimiser
"""
import pandas as pd
import qis as qis
# project
from optimalportfolios import LassoModelType, LassoModel, CovarEstimator, CovarEstimatorType
from mac_portfolio_optimizer.data.db_loader import load_mac_universe_data_from_db
from mac_portfolio_optimizer.core.current_portfolio_optimiser import run_current_saa_taa_portfolios

# fetch data from db
universe_data = load_mac_universe_data_from_db()

# set valuation time periods
time_period = qis.TimePeriod('31Dec2004', '31Mar2025')
saa_valuation_date = pd.Timestamp('31Mar2025')
taa_valuation_date = pd.Timestamp('30Apr2025')

# set model params
lasso_model = LassoModel(model_type=LassoModelType.GROUP_LASSO_CLUSTERS,
                         group_data=None,
                         demean=True,
                         reg_lambda=1e-5,  # 1e-5
                         span=36,
                         solver='ECOS_BB')

covar_estimator = CovarEstimator(covar_estimator_type=CovarEstimatorType.LASSO,
                                 lasso_model=lasso_model,
                                 factor_returns_freq='ME',
                                 rebalancing_freq='ME',  # taa rebalancing
                                 returns_freqs=universe_data.get_joint_rebalancing_freqs(),
                                 span=lasso_model.span,
                                 is_apply_vol_normalised_returns=False,
                                 squeeze_factor=0.0,
                                 residual_var_weight=1.0,
                                 span_freq_dict={'ME': lasso_model.span, 'QE': lasso_model.span},
                                 num_lags_newey_west_dict=None
                                 )

group_max_turnover_constraint = pd.Series({0: 1.0, 1: 0.25, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1})
meta_params = dict(group_tracking_err_vol_constraint=universe_data.set_group_uniform_tracking_error_constraint(
    tracking_err_vol_constraint=0.025),
    global_max_turnover_constraint=None,
    group_max_turnover_constraint=group_max_turnover_constraint,
    is_saa_benchmark_for_betas=False,  # important
    is_joint_saa_taa_covar=True)

taa_weights_0 = universe_data.get_taa_current_weights()

# run optimiser
saa_taa_portfolios = run_current_saa_taa_portfolios(universe_data=universe_data,
                                                    time_period=time_period,
                                                    saa_valuation_date=saa_valuation_date,
                                                    taa_valuation_date=taa_valuation_date,
                                                    taa_weights_0=taa_weights_0,
                                                    **meta_params)

# get data outputs
outputs_dict = saa_taa_portfolios.get_output_dict()

# save outputs to db and locally
from mac_portfolio_optimizer.local_path import OUTPUT_PATH
qis.save_df_to_excel(data=outputs_dict,
                     file_name='prod_portfolio',
                     add_current_date=True,
                     local_path=OUTPUT_PATH)
