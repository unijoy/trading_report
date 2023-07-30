import plotly
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go

pio.templates.default = "plotly_white"


def html_covr(data, freq):
    data_cov_mat = data.cov()
    data_cov_mat_annu = data_cov_mat * freq  # Annualize the co-variance matrix

    # mask = np.where(data_cov_mat_annu == 0, False, True)
    heatmap_trace = go.Heatmap(
        z=data_cov_mat_annu,
        x=data_cov_mat_annu.columns,
        y=data_cov_mat_annu.columns,
        colorscale=px.colors.diverging.RdBu,
        zmin=-1,
        zmax=1
    )
    layout = go.Layout(title="Heatmap Example")

    html = plotly.offline.plot({"data": [heatmap_trace], "layout": layout},
                               include_plotlyjs=False,
                               output_type='div')

    return html, '个股之间的运动关系，1同涨同跌，0无关', None
    # return data_cov_mat_annu.to_html(classes="table table-hover table-bordered table-striped")
