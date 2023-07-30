import numpy as np
import pandas as pd
from base.metrics import ann_geo_mean, ann_std, max_drawdown, ann_sr, ann_ret
import plotly
import plotly.graph_objs as go


# Functions to calculate the portfolio return for back-testing given portfolio weight
# Return the portfolio return over the full back-testing period
# Buy-and-hold strategy
def portRet_BH(w, data_BT):
    n = data_BT.shape[0]
    PR = np.zeros(n)
    X = w * 1  # initial wealth assume to be 1
    for i in range(n):
        W = (1 + data_BT.iloc[i]) @ X  # wealth after each period
        PR[i] = (W - np.sum(X)) / np.sum(X)  # calculate and record portfolio return for that period
        X = (1 + data_BT.iloc[i]) * X  # how much of the wealth is invested in each asset
    return PR


# Function to display the summary statistics of the back test results
# It takes in the portfolio returns dataframe and returns the mean and standard deviation of the portfolio returns
def DisplaySummary_BT(portfolio_returns, rf, freq, n_dec=2):  # TBill_BT['T-Bill']
    col_names = portfolio_returns.columns

    # Compute and display summary statistics for each portfolio
    PR_mean = portfolio_returns.mean()
    PR_std = portfolio_returns.std()
    BT = pd.DataFrame(index=col_names)
    BT['Geo Mean(Annu,%)'] = np.round(portfolio_returns.apply(ann_geo_mean, freq=freq) * 100, n_dec)
    BT['Std(Annu,%)'] = np.round(ann_std(portfolio_returns.std(), freq=freq) * 100, n_dec)
    BT['Sharpe Ratio (Annu)'] = np.round(portfolio_returns.apply(ann_sr, rf=rf, freq=freq), n_dec)
    BT['Max Drawdown(%)'] = np.round(portfolio_returns.apply(max_drawdown) * 100, n_dec)

    return PR_mean, PR_std, BT


# Calculate the weekly portfolio return for each asset mix in df_alloc_r
# (note: takes a bit time for this block to run)
def portfolio_returns_by_weights(data_BT, DF_Alloc_R):
    col_names = DF_Alloc_R.columns
    PR_BH = pd.DataFrame(index=data_BT.index, columns=col_names)
    for i in range(len(col_names)):
        w = DF_Alloc_R.iloc[:, i].values
        PR_BH[col_names[i]] = portRet_BH(w, data_BT)

    return PR_BH


def html_buy_and_hold(data, benchmark, rf, DF_Alloc_R, freq):
    BT_startdate = str(data.index[0].date())
    BT_enddate = str(data.index[-1].date())
    # Trim dataset to have the specified start and end dates for the historical back test
    data_BT = data[BT_startdate:BT_enddate].copy()
    SP500_BT = benchmark[BT_startdate:BT_enddate].copy()

    # Add the equal weighted portfolio to our portfolio allocation dataframe
    n_stocks = len(data_BT.columns)
    w_EQ = np.array(np.ones(n_stocks)) / n_stocks
    DF_Alloc_R['Equal'] = w_EQ

    PR_BH = portfolio_returns_by_weights(data_BT, DF_Alloc_R)

    # Display Results for Buy-and_Hold strategy
    print('Using Buy-and-Hold strategy: Done')
    PR_BH_mean, PR_BH_std, BT = DisplaySummary_BT(PR_BH, rf, freq)
    html = f'<p>Using Buy-and-Hold strategy: </p> <br>' \
           f'<p>Summary statistic of various allocations for the back test ' \
           f'(from {str(BT_startdate)} to {str(BT_enddate)}):</p><br>' \
           f' {BT.to_html(classes="table table-hover table-bordered table-striped")}'

    num_rbar = np.sum(PR_BH.columns.str.contains('%', case=False))
    x = ann_std(PR_BH_std[:num_rbar], freq)
    y = ann_ret(PR_BH_mean[:num_rbar], freq)
    line_trace = go.Scatter(x=x, y=y, mode='lines+markers', line=dict(dash='dash'), name='Efficient Frontier')

    # max sharpe ratio
    sharpe_trace = go.Scatter(x=[ann_std(PR_BH_std['maxSR'], freq)], y=[ann_ret(PR_BH_mean['maxSR'], freq)],
                              mode='markers',
                              marker=dict(symbol='star', size=10), name='Max Shape Ratio')

    # equal weight
    equal_trace = go.Scatter(x=[ann_std(PR_BH_std['Equal'], freq)], y=[ann_ret(PR_BH_mean['Equal'], freq)],
                             mode='markers',
                             marker=dict(symbol='star', size=10), name='Equal Weight')

    # idx sp500
    idx_trace = go.Scatter(x=ann_std(SP500_BT.std(), freq), y=ann_ret(SP500_BT.mean(), freq), mode='markers',
                           marker=dict(symbol='star', size=10), name=benchmark.columns[0])
    # Create a layout
    layout = go.Layout(
        title='Ex-Post Mean-Variance Plot via Buy-and-Hold (' + str(BT_startdate) + ' to ' + str(BT_enddate) + ')')
    html = html + plotly.offline.plot({"data": [line_trace, equal_trace, idx_trace, sharpe_trace], "layout": layout},
                                      include_plotlyjs=False,
                                      output_type='div')

    return html, '策略 Buy and Hold', None
