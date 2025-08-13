import pandas as pd
import qis as qis
import seaborn as sns
import matplotlib.pyplot as plt

data = {
  12: [0.86, 0.78, 0.79, 0.73, 0.77, 0.76, 0.76],
  24: [0.81, 0.82, 0.78, 0.78, 0.76, 0.76, 0.76],
  36: [0.78, 0.82, 0.80, 0.76, 0.76, 0.76, 0.76],
  48: [0.81, 0.81, 0.82, 0.80, 0.77, 0.77, 0.77]
}
sharpe = pd.DataFrame(data)
sharpe.index = ['1e-3', '1e-4', '1e-5', '1e-6', '1e-7', '1e-8', '0']
sharpe.loc['1e-3', :] *= 0.9
print(sharpe)

data = {
  12: [-25, -25.25, -25.5, -25.75, -26, -26.25, -26.5],
  24: [-19, -23.25, -23.5, -24.25, -24.5, -25.25, -25.5],
  36: [-21, -22.25, -22.5, -24.1, -24.2, -24.3, -24.4],
  48: [-20, -21, -21, -22, -24, -24, -24]
}
max_dd = pd.DataFrame(data) / 100.0
max_dd.index = ['1e-3', '1e-4', '1e-5', '1e-6', '1e-7', '1e-8', '0']
print(max_dd)

sharpe = pd.melt(sharpe, value_vars=sharpe.columns, var_name='hue',
                 value_name='sharpe')

max_dd = pd.melt(max_dd, value_vars=max_dd.columns, var_name='hue',
                 value_name='max_dd')
df = pd.concat([sharpe, max_dd], axis=1)
df = df.loc[:, ~df.columns.duplicated(keep='first')]

print(df)

with sns.axes_style('darkgrid'):
    fig, ax = plt.subplots(1, 1, figsize=(16, 8), constrained_layout=True)
    # qis.plot_scatter(df=df, x='max_dd', y='sharpe', hue='hue', order=0, ax=ax)

    sns.lineplot(data=df, x='max_dd', y='sharpe', hue='hue', ax=ax)

plt.show()
