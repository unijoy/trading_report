from datetime import datetime


# this func return current date
def current_date():
    return datetime.now().strftime('%Y-%m-%d')


# only for testing purpose
def html_row():
    html_tpl = f"""
    <div class="row"><h5>Generate Date</h5></div>
    <div class="row">
        <div class="col-sm-12">
            {current_date()}
        </div>
    </div>
    """
    return html_tpl, '生成日期', None
