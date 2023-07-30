from base.metrics import alpha_beta


def html_alpha_beta(data, rf, benchmark, freq):
    AlphaBeta = alpha_beta(data=data, benchmark=benchmark, rf=rf, freq=freq)
    return AlphaBeta.to_html(
        classes="table table-hover table-bordered table-striped"), '个股与index之间的线性关系', None
