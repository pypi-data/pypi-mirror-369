import pandas as pd
import numpy as np
import qis as qis
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict
from enum import Enum

from mac_portfolio_optimizer import load_mac_portfolio_universe, SaaPortfolio, TaaPortfolio


class LocalTests(Enum):
    BLACKROCK_CMAS = 1


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
    local_path_out = "C://Users//artur//OneDrive//My Papers//Working Papers//Multi-Asset Allocation. Zurich. Dec 2024//Figures//"
    # local_path_out = lp.get_output_path()

    is_funds_universe = False
    if is_funds_universe:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_MAC,
                                                    taa_portfolio=TaaPortfolio.TAA_FUNDS_MAC)
    else:
        universe_data = load_mac_portfolio_universe(local_path=local_path,
                                                    saa_portfolio=SaaPortfolio.SAA_INDEX_PAPER,
                                                    taa_portfolio=TaaPortfolio.TAA_INDEX_PAPER)

    time_period = qis.TimePeriod('31Dec2004', '31Mar2025')

    if local_test == LocalTests.BLACKROCK_CMAS:
        df_cmas = qis.load_df_from_excel(file_name='blackrock-capital-market-assumptions', sheet_name='Starting point scenario',
                                         local_path=local_path)
        df_cmas = df_cmas.loc[:, ~df_cmas.columns.duplicated(keep='first')]
        df_cmas = df_cmas.loc[df_cmas.index == 'USD', :]
        df_cmas = df_cmas.reset_index().set_index('Asset')
        df_cmas['Asset class'] = df_cmas['Asset class'].replace({'Private markets': 'Alternatives'})
        print(df_cmas)

        with sns.axes_style("darkgrid"):
            fig, ax = plt.subplots(1, 1, figsize=(12, 8), tight_layout=True)

            annotation_labels = df_cmas.index.to_list()
            ac_colors = {'Alternatives': 'orange', 'Equities': 'green', 'Fixed income': 'olive'}
            ac_markers = {'Alternatives': 'o', 'Equities': 'v', 'Fixed income': 's'}
            annotation_colors = df_cmas['Asset class'].map(ac_colors).to_list()
            annotation_markers = df_cmas['Asset class'].map(ac_markers).to_list()
            kwargs = dict(fontsize=12, framealpha=0.95)
            qis.plot_scatter(df=df_cmas,
                             x='Volatility',
                             y='5 year',
                             ylabel='Expected annual return over next 5y period',
                             # hue='Asset class',
                             xvar_format='{:.1%}',
                             yvar_format='{:.1%}',
                             add_universe_model_label=True,
                             annotation_labels=annotation_labels,
                             annotation_colors=annotation_colors,
                             annotation_markers=annotation_markers,
                             order=1,
                             full_sample_order=1,
                             ci=95,
                             full_sample_label='Regression:',
                             x_limits=(0.0, None),
                             legend_loc='upper left',
                             ax=ax,
                             **kwargs)
            ax2 = ax.twinx()
            ax2.get_yaxis().set_visible(False)
            qis.set_legend(ax=ax2, labels=list(ac_colors.keys()), colors=list(ac_colors.values()),
                           markers=list(ac_markers.values()),
                           loc='upper left',
                           handlelength=0,
                           bbox_to_anchor=(0.0, 0.975),
                           text_weight='normal',
                           **kwargs)
            qis.save_fig(fig, file_name='blackrock_cmas', local_path=local_path_out)

    plt.show()


if __name__ == '__main__':

    run_local_test(local_test=LocalTests.BLACKROCK_CMAS)
