import os

from jinja2 import Environment, FileSystemLoader
from base.dynamic_run import dynamic_funcs
from debug_data_loader import load_data


# original source from
# https://pythonforfinance.net/2019/02/03/trading-strategy-performance-report-in-python-part-4/
# change it to dynamic
class PerformanceReport:
    """ Report with performance stats for given strategy returns.
    """

    def __init__(self, data, func, out_file='performance_report.html',
                 tpl="templates/template_simple.html"):
        self.out_file = out_file
        self.tpl = tpl
        self.data = data
        self.dynamic_func = func
        self.dict_parameters = {}

    def generate_html(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(self.tpl)
        if self.dynamic_func is not None:
            self.dict_parameters = self.dynamic_func(self.data)
        html_out = template.render(my_dict=self.dict_parameters)
        return html_out

    def generate_html_report(self):
        """ Returns HTML report with analysis
        """
        html = self.generate_html()
        outputdir = "output"
        os.makedirs(outputdir, exist_ok=True)

        outfile = os.path.join(outputdir, self.out_file)
        with open(outfile, 'w') as file:
            file.write(html)



if __name__ == "__main__":
    data = load_data()

    report = PerformanceReport(data, dynamic_funcs, out_file="test.html", tpl="template_simple.html")
    report.generate_html_report()
