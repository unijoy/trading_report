from base.metrics import summary


def html_summary_statistics_info(data, rf, freq):
    return summary(data, rf, freq).to_html(
        classes="table table-hover table-bordered table-striped"), '基本指标', None
