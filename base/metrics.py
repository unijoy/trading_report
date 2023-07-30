import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression  # for solving linear regression
# pd.set_option('float_format', '{:.4f}'.format)

def ann_ret(x, freq):
    """

    :param x: Average Return
    :param freq: 250  frequency factor (given weekly data, it is 52)
    :return: Functions for annualizing returns and standard deviation
    """
    return (x + 1) ** freq - 1


def ann_std(x, freq):
    return x * np.sqrt(freq)


# 年化复合增长率compounded annual growth rate (CAGR) of an investment over a period of time.
# 相当于公式：(1 + Total Return)^(freq/n) - 1
# Function used to find the Annualized geometric mean of x [note: x is weekly data]
def ann_geo_mean(x, freq):
    n = len(x)
    return np.exp(np.sum(np.log(1 + x)) * freq / n) - 1


# 相当于：(1 + Average Weekly Return)^freq - 1
# Function used to find the annualized arithmetic mean
def ann_arithmetic_mean(x, freq):
    return ann_ret(np.mean(x), freq)


# Function used to find the Annualized Sharpe Ratio of x
def ann_sr(x, rf, freq):
    n = len(x)
    excess_returns = x - rf
    ret_expected = np.sum(excess_returns) / n
    # ret_avg = np.sum(x) / n
    std_dev = np.sqrt(np.sum((excess_returns - ret_expected) ** 2) / n)
    annu_ret_expected = (ret_expected + 1) ** freq - 1
    annu_std_dev = std_dev * np.sqrt(freq)
    return annu_ret_expected / annu_std_dev


# Function used to find the Maximum drawdown
def max_drawdown(x):
    wealth = (x + 1).cumprod()  # x is a return vector
    cummax = wealth.cummax()  # determine cumulative maximum value
    drawdown = wealth / cummax - 1  # calculate drawdown vector
    return drawdown.min()

    # 完整性检查


# Output summary statistics information:rf=TBill['T-Bill']
# Calculate and show the Mean, Geometric Mean, and Standard Deviation, Sharpe Ratio, Maximum Drawdown (with 2 decimals)
def summary(data, rf, freq, n_dec=2):
    if data.isnull().values.any():
        print('WARNING: Some firms have missing data during this time period!')
        print('Dropping firms: ')
        for Xcol_dropped in list(data.columns[data.isna().any()]): print(Xcol_dropped)
        data = data.dropna(axis='columns')

    SumStat = pd.DataFrame(index=data.columns)
    SumStat['Total Return(%)'] = np.round((((data + 1).cumprod() - 1) * 100).iloc[-1], n_dec)
    SumStat['Geo Mean(Annu,%)'] = np.round(data.apply(ann_geo_mean, args=(freq,)) * 100, n_dec)
    SumStat['Arithmetic Mean(Annu,%)'] = np.round(data.apply(ann_arithmetic_mean, freq=freq) * 100, n_dec)
    SumStat['Volatility(Annu,%)'] = np.round(ann_std(data.std(), freq=freq) * 100, n_dec)
    SumStat['Sharpe Ratio (Annu)'] = np.round(data.apply(ann_sr, rf=rf, freq=freq), n_dec)
    SumStat['Max Drawdown(%)'] = np.round(data.apply(max_drawdown) * 100, n_dec)
    return SumStat


# Function for performing linear regression and returning coefficient as well as intercept
def LR(X, y):
    reg = LinearRegression().fit(X.reshape(-1, 1), y.reshape(-1, 1))  # perform linear regression
    return reg.coef_, reg.intercept_


def alpha_beta(data, benchmark, rf, freq):
    # Calculate and display alpha and beta for each stock
    n_dec = 3  # rounding to this decimal places

    # Get excess returns of the stocks and the market
    ex_ret = data.sub(rf, axis=0)
    mkt_ex_ret = benchmark.sub(rf, axis=0)

    # Calculate the alpha and beta for each stock
    n = len(ex_ret.columns)
    beta = np.zeros(n)
    alpha = np.zeros(n)
    for i in range(n):
        beta[i], alpha[i] = LR(mkt_ex_ret.values, ex_ret[ex_ret.columns[i]].values)

    # Display the alpha and beta information
    AlphaBeta = pd.DataFrame(index=data.columns)
    AlphaBeta['Alpha(Annu,%)'] = np.round(ann_ret(alpha, freq) * 100, n_dec)
    AlphaBeta['Beta'] = np.round(beta, n_dec)
    return AlphaBeta


# Covariance Matrix of Returns
def covriance(data, freq):
    # Calculate and output the covariance matrix for the stock returns
    data_cov_mat = data.cov()
    data_cov_mat_annu = data_cov_mat * freq  # Annualize the co-variance matrix
    print("The Annualized Covariance matrix (for the weekly returns) is: ")
    return data_cov_mat_annu


# Plot cumulative return for each firm
def cumulative_return_plot(df_returns, colors, show=False):
    import plotly
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots
    from plotly.offline import plot

    df = (df_returns + 1).cumprod()

    lo_col = 4
    lo_row = int(np.ceil(len(df.columns) / 4))
    # Create the subplots
    fig = make_subplots(rows=lo_row, cols=lo_col, shared_xaxes=True, shared_yaxes=True, row_heights=[300] * lo_row)

    # Add traces to the subplots
    for i in range(0, len(df.columns)):
        if colors is not None:
            arr = np.array(colors[i])
            r = int(arr[0] * 255)
            g = int(arr[1] * 255)
            b = int(arr[2] * 255)
            hex_string = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            fig.add_trace(go.Scatter(x=df.index, y=df[df.columns[i]], name=df.columns[i], line=dict(color=hex_string)),
                          row=int(np.floor(i / 4) + 1),
                          col=int(i % 4 + 1),
                          )
        else:
            fig.add_trace(go.Scatter(x=df.index, y=df[df.columns[i]], name=df.columns[i]),
                          row=int(np.floor(i / 4) + 1),
                          col=int(i % 4 + 1)
                          )
    # Set the layout of the subplots
    fig.update_layout(title='cumulative return for each firm',
                      yaxis={'type': 'log', 'title': 'Y-axis (log scale)'},
                      height=300 * lo_row
                      )

    # Create an HTML file with the plot
    if show:
        plot(fig, filename='cumulative_return_plot.html')
        return None
    else:
        return plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')


if __name__ == '__main__':
    file_name = 'CleanedData_Weekly.xlsx'
    sheet_name = 'Stock Returns'
    df = pd.read_excel(file_name, sheet_name, index_col=0, engine='openpyxl')
    df.index = pd.to_datetime(df.index)
    data = df.copy()
    cumulative_return_plot(data, show=True)
