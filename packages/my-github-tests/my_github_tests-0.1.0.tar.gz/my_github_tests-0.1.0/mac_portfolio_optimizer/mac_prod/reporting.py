"""
implement common reporting
"""
import qis as qis
import matplotlib.pyplot as plt
from typing import Optional
from optimalportfolios import AlphasData, EstimatedRollingCovarData
from mac_portfolio_optimizer import MacUniverseData


def generate_report(multi_portfolio_data: qis.MultiPortfolioData,
                    universe_data: MacUniverseData,
                    taa_covar_data: EstimatedRollingCovarData,
                    time_period: qis.TimePeriod,
                    file_name: str,
                    local_path: str,
                    manager_alphas: Optional[AlphasData] = None,
                    apply_sub_ac_group_data: bool = True,
                    save_figures_png: bool = False,
                    save_excel: bool = True
                    ) -> None:

    report_kwargs = qis.fetch_default_report_kwargs(time_period=time_period,
                                                    reporting_frequency=qis.ReportingFrequency.QUARTERLY,
                                                    add_rates_data=False)
    report_kwargs = qis.update_kwargs(report_kwargs, dict(ytd_attribution_time_period=qis.TimePeriod('30Jun2024', '30Jun2025')))

    figs1 = qis.generate_strategy_benchmark_factsheet_plt(multi_portfolio_data=multi_portfolio_data,
                                                          strategy_idx=0,
                                                          # strategy is multi_portfolio_data[strategy_idx]
                                                          benchmark_idx=1,
                                                          add_benchmarks_to_navs=True,
                                                          add_exposures_comp=False,
                                                          add_strategy_factsheet=True,
                                                          time_period=time_period,
                                                          **report_kwargs)
    plt.close('all')
    # generate tre figures
    report_kwargs = qis.update_kwargs(report_kwargs, dict(framealpha=0.9))  # , x_date_freq='YE'

    # get linear model
    risk_model = taa_covar_data.get_linear_factor_model(x_factors=universe_data.get_risk_factors(),
                                                        y_assets=universe_data.get_joint_prices())

    if apply_sub_ac_group_data:
        ac_group_data, ac_group_order = universe_data.get_joint_ac_group_data()
        sub_ac_group_data, sub_ac_group_order = universe_data.get_joint_sub_ac_group_data()
        sub_ac_group_data = sub_ac_group_data
        sub_ac_group_order = sub_ac_group_order
        turnover_groups = universe_data.get_joint_turnover_groups()
        turnover_order = universe_data.get_joint_turnover_order()
    else:
        ac_group_data, ac_group_order = universe_data.get_saa_asset_class_data(), universe_data.ac_group_order
        sub_ac_group_data = ac_group_data
        sub_ac_group_order = ac_group_order
        turnover_groups = universe_data.get_saa_turnover_groups()
        turnover_order = universe_data.get_joint_turnover_order()

    figs2, dfs = qis.weights_tracking_error_report_by_ac_subac(multi_portfolio_data=multi_portfolio_data,
                                                               time_period=time_period,
                                                               ac_group_data=ac_group_data,
                                                               ac_group_order=ac_group_order,
                                                               sub_ac_group_data=sub_ac_group_data,
                                                               sub_ac_group_order=sub_ac_group_order,
                                                               turnover_groups=turnover_groups,
                                                               turnover_order=turnover_order,
                                                               risk_model=risk_model,
                                                               **report_kwargs)
    if save_figures_png:
        qis.save_figs(figs=figs2, file_name=file_name, local_path=local_path)

    for k, fig in figs2.items():
        figs1.append(fig)
    qis.save_figs_to_pdf(figs1, file_name=file_name, local_path=local_path)

    if save_excel:
        taa_weights = multi_portfolio_data.portfolio_datas[0].get_input_weights()[universe_data.taa_prices.columns]
        returns = qis.to_returns(multi_portfolio_data.get_navs(time_period=time_period), freq='ME')
        data = dict(returns=returns,
                    taa_weights=taa_weights,
                    saa_weights=multi_portfolio_data.portfolio_datas[1].get_input_weights(),
                    taa_prices=universe_data.taa_prices,
                    saa_prices=universe_data.saa_prices,
                    saa_description=universe_data.saa_universe_df,
                    taa_description=universe_data.taa_universe_df,
                    risk_factors_prices=universe_data.get_risk_factors())
        if manager_alphas is not None:
            data.update(manager_alphas.to_dict())
        data.update(dfs)
        qis.save_df_to_excel(data=data,
                             file_name=file_name,
                             add_current_date=True, local_path=local_path)

