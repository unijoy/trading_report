import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go

from base.max_sharperatio import MaxSR
from base.metrics import ann_ret, ann_std
from base.Efficient_Frontier import gen_bars, run
from base.markowitz import MarkPortOpt, PVol,EReturn
from base.markowitz_rf import MarkPortOpt_with_rf

def html_efficient_frontier(data, rf, freq):
    symbos = data.columns

    # Join the stock returns dataframe with T-Bill return dataframe
    data_train_with_rf = data.copy()
    data_train_with_rf = data_train_with_rf.join(rf)

    data_train_mean = data.mean()
    data_train_cov_mat = data.cov()

    data_train_with_rf_cov_mat = data_train_with_rf.cov()
    r_bar = gen_bars(freq=freq)

    alloc_r, port_return, port_vol = run(data, r_bar, MarkPortOpt)
    alloc_r_with_rf, port_return_with_rf, port_vol_with_rf = run(data_train_with_rf, r_bar, MarkPortOpt_with_rf)

    # Display the optimal allocation for each specified target return
    DF_Alloc_R = pd.DataFrame(alloc_r)
    DF_Alloc_R.index = symbos
    DF_Alloc_R.columns = [str(round(ann_ret(r, freq) * 100, 1)) + "%" for r in r_bar]
    DF_Alloc_R = DF_Alloc_R.loc[:,
                 (DF_Alloc_R != 0).any(axis=0)]  # drop the r-bar solution(s) that failed the opt. problem

    # -----------------
    # Find the optimal portfolio that maximize Sharpe Ratio
    sol, sr = MaxSR(data=data, rf=rf, freq=freq, data_cov_mat=data_train_cov_mat)
    w_SR = sol['x']  # the portfolio weight with highest Sharpe Ratio

    # Calculate the volatility and expected return for the optimal portfolio
    opt_vol = PVol(sol['x'], data_train_cov_mat)
    opt_return = EReturn(sol['x'], data_train_mean)
    # sr = AnnSR(sol['x'])

    # Print (annualized) return, volatiltiy and Sharpe ratio information
    html = f'<p>* The expected return (annualized) for the optimal portfolio is {ann_ret(opt_return, freq):.4f}</p><br>' \
           f'<p>* The volatility (annualized) for the optimal portfolio is {ann_std(opt_vol, freq):.4f}</p><br>' \
           f'<p>* The Sharpe ratio (annualized) for the optimal portfolio is {sr:.4f}</p><br>'

    DF_Alloc_R['maxSR'] = w_SR
    # -----------------

    html = html + '<p>Optimal allocation (in %) for specified (annualized) target return:</p>'
    # display(np.round(DF_Alloc_R * 100, 1))  # allocation in % and round (to the 1st decimal)
    html = html + np.round(DF_Alloc_R * 100, 1).to_html(classes="table table-hover table-bordered table-striped")
    html = html + "<br>"
    # for debug............
    DF_Alloc_R_with_rf = pd.DataFrame(alloc_r_with_rf)
    DF_Alloc_R_with_rf.index = data_train_with_rf.columns
    DF_Alloc_R_with_rf.columns = [str(round(ann_ret(r, freq) * 100, 1)) + "%" for r in r_bar]
    DF_Alloc_R_with_rf = DF_Alloc_R_with_rf.loc[:,
                         (DF_Alloc_R_with_rf != 0).any(axis=0)]
    html = html + np.round(DF_Alloc_R_with_rf * 100, 1).to_html(
        classes="table table-hover table-bordered table-striped")

    x = ann_std(port_vol, freq)
    y = ann_ret(port_return, freq)
    x2 = ann_std(port_vol_with_rf, freq)
    y2 = ann_ret(port_return_with_rf, freq)

    # Create a line trace
    line_trace = go.Scatter(x=x, y=y, mode='lines+markers', line=dict(dash='dash'), name='Efficient Frontier')

    line_trace2 = go.Scatter(x=x2, y=y2, mode='lines+markers', line=dict(dash='dash'), name='with Risk free')

    sharpe_trace = go.Scatter(x=[ann_std(opt_vol, freq)], y=[ann_ret(opt_return, freq)], mode='markers',
                              marker=dict(symbol='star', color='green', size=10), name='Max Shape Ratio')
    # Create a layout
    layout = go.Layout(title="Efficient Frontier")
    html = html + plotly.offline.plot({"data": [line_trace, line_trace2, sharpe_trace], "layout": layout},
                                      include_plotlyjs=False,
                                      output_type='div')

    # --------------------
    # Calculate the portfolio weight (90% max Sharpe + 10% risk-free rate)
    w_port1 = np.append(0.9 * w_SR, 0.1)

    # Calculate the portfolio risk
    risk_port1 = np.sqrt(w_port1 @ data_train_with_rf_cov_mat @ w_port1)

    html = html + '<p>Calculate the portfolio weight (90% max Sharpe + 10% risk-free rate)</p><br> ' \
                  f'<p>The new portfolio risk (annualized) is:{ann_std(risk_port1, freq):.4f} </p><br>' \
                  f'<p>The portfolio risk (annualized) for the max Sharpe point was:{ann_std(PVol(w_SR, data_train_cov_mat), freq):.4f} </p><br>'
    # --------------------

    # html = html + buy_and_hold(data, SP500=SP500, TBill=TBill, DF_Alloc_R=DF_Alloc_R, freq=freq)

    return html, 'Efficient Frontier', {'DF_Alloc_R': DF_Alloc_R}